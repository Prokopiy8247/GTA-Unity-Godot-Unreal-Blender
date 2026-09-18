using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace Meridian.Editor {
public static class ReleaseBuilder {
    static void Configure() {
        Directory.CreateDirectory(".astra-run");
        PlayerSettings.companyName = "Meridian Studio";
        PlayerSettings.productName = "Meridian Coast";
        PlayerSettings.bundleVersion = "1.0.0";
        PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Standalone, "com.meridianstudio.meridiancoast");
        PlayerSettings.SetScriptingBackend(NamedBuildTarget.Standalone, ScriptingImplementation.Mono2x);
        PlayerSettings.fullScreenMode = FullScreenMode.FullScreenWindow;
        PlayerSettings.defaultIsNativeResolution = true;
        PlayerSettings.resizableWindow = true;
        PlayerSettings.allowFullscreenSwitch = true;
        PlayerSettings.runInBackground = true;
        EditorUserBuildSettings.development = false;
        EditorUserBuildSettings.allowDebugging = false;
        AssetDatabase.SaveAssets();
    }
    [MenuItem("Meridian/Release/Build Windows")]
    public static void Windows() {
        Configure();
        PlayerSettings.SetArchitecture(NamedBuildTarget.Standalone, 0);
        Build(BuildTarget.StandaloneWindows64, "Builds/Windows/MeridianCoast.exe", "windows");
    }
    [MenuItem("Meridian/Release/Build macOS Universal")]
    public static void MacOS() {
        Configure();
        var settingsType = Type.GetType("UnityEditor.OSXStandalone.UserBuildSettings, UnityEditor.OSXStandalone.Extensions");
        var architecture = settingsType?.GetProperty("architecture", System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static);
        if (architecture == null) throw new InvalidOperationException("Install macOS Build Support in Unity Hub.");
        architecture.SetValue(null, Enum.Parse(architecture.PropertyType, "x64ARM64"));
        Debug.Log("macOS target architecture: " + architecture.GetValue(null));
        Build(BuildTarget.StandaloneOSX, "Builds/macOS/Meridian Coast.app", "macos");
    }
    static void Build(BuildTarget target, string output, string name) {
        Directory.CreateDirectory(Path.GetDirectoryName(output));
        var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions {
            scenes = new[] { "Assets/GTA/Scenes/Meridian_FreeRoam.unity" },
            locationPathName = output,
            target = target,
            options = BuildOptions.CompressWithLz4HC
        });
        var messages = report.steps.SelectMany(s => s.messages)
            .Where(m => m.type == LogType.Warning || m.type == LogType.Error)
            .Select(m => m.type + ": " + m.content);
        File.WriteAllText(".astra-run/release-" + name + ".txt",
            report.summary.result + "\nErrors: " + report.summary.totalErrors +
            "\nWarnings: " + report.summary.totalWarnings + "\nBytes: " + report.summary.totalSize +
            "\nDuration: " + report.summary.totalTime + "\n" + string.Join("\n", messages));
        if (report.summary.result != BuildResult.Succeeded)
            throw new Exception("Release build failed: " + name);
        Debug.Log("MERIDIAN_RELEASE_SUCCESS " + name);
    }
}
}
