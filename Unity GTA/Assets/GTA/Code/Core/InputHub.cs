using UnityEngine;
using UnityEngine.InputSystem;
namespace Meridian {
public static class InputHub {
 public static bool scripted; public static Vector2 simulatedMove; public static float simulatedLift; public static bool simulatedBrake;
 public static bool Down(Key k)=>!scripted&&Keyboard.current!=null&&Keyboard.current[k].wasPressedThisFrame;
 public static bool Held(Key k)=>!scripted&&Keyboard.current!=null&&Keyboard.current[k].isPressed;
 public static Vector2 Move=>scripted?simulatedMove:new Vector2((Held(Key.D)?1:0)-(Held(Key.A)?1:0),(Held(Key.W)?1:0)-(Held(Key.S)?1:0));
 public static Vector2 Look=>scripted||Mouse.current==null?Vector2.zero:Mouse.current.delta.ReadValue();
 public static bool Fire=>!scripted&&Mouse.current!=null&&Mouse.current.leftButton.isPressed;
 public static bool FireDown=>!scripted&&Mouse.current!=null&&Mouse.current.leftButton.wasPressedThisFrame;
 public static bool Aim=>!scripted&&Mouse.current!=null&&Mouse.current.rightButton.isPressed;
 public static float Scroll=>scripted||Mouse.current==null?0:Mouse.current.scroll.ReadValue().y;
 public static float Lift=>scripted?simulatedLift:(Held(Key.Space)?1:0)-(Held(Key.LeftCtrl)?1:0);
}
}
