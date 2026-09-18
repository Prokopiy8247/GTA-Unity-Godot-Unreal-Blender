using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace Meridian.Editor {
// CodeView records can retain the developer's absolute PDB path even without shipping a PDB.
// Normalize only that metadata, before Unity packages and signs the player.
public sealed class PublicDebugMetadata : IPostBuildPlayerScriptDLLs {
    public int callbackOrder => 10000;
    public void OnPostBuildPlayerScriptDLLs(BuildReport report) {
        var candidates = new HashSet<string>();
        foreach (var file in report.GetFiles())
            if (Path.GetFileName(file.path) == "Assembly-CSharp.dll" && File.Exists(file.path)) candidates.Add(file.path);
        foreach (var root in new[] { "Library/Bee/PlayerScriptAssemblies", "Library/PlayerScriptAssemblies" })
            if (Directory.Exists(root))
                foreach (var file in Directory.GetFiles(root, "Assembly-CSharp*.dll")) candidates.Add(file);
        int changed = 0;
        foreach (var file in candidates) if (Normalize(file)) changed++;
        Debug.Log("Public debug metadata normalized in " + changed + " player assemblies.");
    }
    static bool Normalize(string path) {
        byte[] b = File.ReadAllBytes(path);
        if (b.Length < 128 || b[0] != 'M' || b[1] != 'Z') return false;
        int pe = BitConverter.ToInt32(b, 0x3c);
        int coff = pe + 4, optional = coff + 20;
        int sections = BitConverter.ToUInt16(b, coff + 2);
        int table = optional + BitConverter.ToUInt16(b, coff + 16);
        int directories = optional + (BitConverter.ToUInt16(b, optional) == 0x20b ? 112 : 96);
        uint rva = BitConverter.ToUInt32(b, directories + 48);
        uint length = BitConverter.ToUInt32(b, directories + 52);
        if (rva == 0 || length == 0) return false;
        int start = -1;
        for (int i = 0; i < sections; i++) {
            int s = table + i * 40;
            uint address = BitConverter.ToUInt32(b, s + 12);
            uint span = Math.Max(BitConverter.ToUInt32(b, s + 8), BitConverter.ToUInt32(b, s + 16));
            if (rva >= address && rva < address + span) start = checked((int)(BitConverter.ToUInt32(b, s + 20) + rva - address));
        }
        if (start < 0) throw new InvalidDataException("Invalid PE debug directory");
        bool changed = false;
        for (int at = start; at + 28 <= start + length; at += 28) {
            if (BitConverter.ToUInt32(b, at + 12) != 2) continue;
            int size = checked((int)BitConverter.ToUInt32(b, at + 16));
            int data = checked((int)BitConverter.ToUInt32(b, at + 24));
            if (size < 25 || data < 0 || data + size > b.Length || Encoding.ASCII.GetString(b, data, 4) != "RSDS") continue;
            string old = Encoding.UTF8.GetString(b, data + 24, size - 24).TrimEnd('\0');
            string name = Path.GetFileName(old.Replace('\\', '/'));
            if (name == old) continue;
            byte[] clean = Encoding.UTF8.GetBytes(name);
            if (clean.Length >= size - 24) throw new InvalidDataException("Unexpected CodeView path size");
            Array.Clear(b, data + 24, size - 24);
            Array.Copy(clean, 0, b, data + 24, clean.Length);
            changed = true;
        }
        if (changed) File.WriteAllBytes(path, b);
        return changed;
    }
}
}
