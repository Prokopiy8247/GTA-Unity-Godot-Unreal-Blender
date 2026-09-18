#include "PMGame.h"
#include "GameFramework/GameUserSettings.h"
#include "AudioDevice.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "InputActionValue.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Components/SpotLightComponent.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Components/ScrollBox.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/TextBlock.h"
#include "Blueprint/WidgetTree.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/LocalPlayer.h"
#include "Engine/Engine.h"
#include "Camera/PlayerCameraManager.h"
#include "Rendering/DrawElements.h"
#include "Styling/CoreStyle.h"

APMPlayer* APMController::Player()const{return Cast<APMPlayer>(GetPawn());}
APMWorld* APMController::Manager()const{return Cast<APMWorld>(UGameplayStatics::GetActorOfClass(this,APMWorld::StaticClass()));}
void APMController::BeginPlay() {
 Super::BeginPlay();bShowMouseCursor=false;SetInputMode(FInputModeGameOnly());
 HUDWidget=CreateWidget<UPMHUD>(this,UPMHUD::StaticClass());if(HUDWidget)HUDWidget->AddToViewport();
 SetControlRotation(FRotator(-8,130,0));ApplyPreferences();
}
void APMController::SetupInputComponent() {
 Super::SetupInputComponent();
 auto E=Cast<UEnhancedInputComponent>(InputComponent);if(!E)return;
 Mapping=NewObject<UInputMappingContext>(this);
 auto Action=[&](FKey Key,const TCHAR* Name,EInputActionValueType Type=EInputActionValueType::Boolean) {
  auto A=NewObject<UInputAction>(this,FName(Name));A->ValueType=Type;Mapping->MapKey(A,Key);Actions.Add(A);return A;
 };
 E->BindAction(Action(EKeys::W,TEXT("Forward"),EInputActionValueType::Axis1D),ETriggerEvent::Triggered,this,&APMController::MoveForward,1.f);
 E->BindAction(Action(EKeys::S,TEXT("Backward"),EInputActionValueType::Axis1D),ETriggerEvent::Triggered,this,&APMController::MoveForward,-1.f);
 E->BindAction(Action(EKeys::D,TEXT("Right"),EInputActionValueType::Axis1D),ETriggerEvent::Triggered,this,&APMController::MoveRight,1.f);
 E->BindAction(Action(EKeys::A,TEXT("Left"),EInputActionValueType::Axis1D),ETriggerEvent::Triggered,this,&APMController::MoveRight,-1.f);
 E->BindAction(Action(EKeys::MouseX,TEXT("LookYaw"),EInputActionValueType::Axis1D),ETriggerEvent::Triggered,this,&APMController::LookYaw);
 E->BindAction(Action(EKeys::MouseY,TEXT("LookPitch"),EInputActionValueType::Axis1D),ETriggerEvent::Triggered,this,&APMController::LookPitch);
 TArray<FKey> Keys={EKeys::F,EKeys::E,EKeys::SpaceBar,EKeys::Q,EKeys::C,EKeys::R,EKeys::V,EKeys::H,EKeys::L,EKeys::Tab,EKeys::P,EKeys::F5,EKeys::F9,EKeys::F1,EKeys::M,EKeys::Escape,EKeys::LeftMouseButton,EKeys::MouseScrollUp,EKeys::MouseScrollDown,EKeys::One,EKeys::Two,EKeys::Three,EKeys::Four,EKeys::Five,EKeys::Six,EKeys::Seven,EKeys::Eight,EKeys::Nine};
 for(int i=0;i<Keys.Num();i++) {
  auto A=Action(Keys[i],*FString::Printf(TEXT("Action%d"),i));
  E->BindAction(A,ETriggerEvent::Started,this,&APMController::Key,i);
  if(i==9)E->BindAction(A,ETriggerEvent::Completed,this,&APMController::Key,1009);
 }
 if(auto LP=GetLocalPlayer())if(auto S=LP->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())S->AddMappingContext(Mapping,0);
}
void APMController::MoveForward(const FInputActionValue& V,float Sign) {
 auto P=Player();if(!P||bMenu||bMap||bPaused||P->Vehicle||P->bDead)return;
 FVector D=FRotationMatrix(FRotator(0,GetControlRotation().Yaw,0)).GetUnitAxis(EAxis::X);
 if(P->bInCover)D=FVector::VectorPlaneProject(D,P->CoverNormal);
 P->AddMovementInput(D,V.Get<float>()*Sign);
}
void APMController::MoveRight(const FInputActionValue& V,float Sign) {
 auto P=Player();if(!P||bMenu||bMap||bPaused||P->Vehicle||P->bDead)return;
 FVector D=FRotationMatrix(FRotator(0,GetControlRotation().Yaw,0)).GetUnitAxis(EAxis::Y);
 if(P->bInCover)D=FVector::CrossProduct(FVector::UpVector,P->CoverNormal);
 P->AddMovementInput(D,V.Get<float>()*Sign);
}
void APMController::LookYaw(const FInputActionValue& V){if(!bMenu&&!bMap&&!bPaused)AddYawInput(V.Get<float>()*1.6f);}
void APMController::LookPitch(const FInputActionValue& V){if(!bMenu&&!bMap&&!bPaused)AddPitchInput(-V.Get<float>()*1.5f);}
void APMController::PlayerTick(float Dt) {
 Super::PlayerTick(Dt);
 auto P=Player();if(!P)return;
 if(bWaypoint&&FVector::Dist2D(P->GetActorLocation(),Waypoint)<700){bWaypoint=false;if(auto W=Manager())W->Message(TEXT("Destination reached"));}
 if(P->Vehicle&&!bMenu&&!P->bAim&&!IsInputKeyDown(EKeys::RightMouseButton)&&!IsInputKeyDown(EKeys::LeftAlt)) {
  float DeltaX=0,DeltaY=0;GetInputMouseDelta(DeltaX,DeltaY);
  if(FMath::Abs(DeltaX)<.01) {
   FRotator R=GetControlRotation();R.Yaw=FMath::FInterpTo(R.Yaw,P->Vehicle->GetActorRotation().Yaw,Dt,1.3);
   SetControlRotation(R);
  }
 }
}
void APMController::Key(const FInputActionValue& V,int32 Id) {
 auto P=Player();if(!P)return;
 if(Id==13){ToggleMenu();return;}
 if(Id==15){if(bPaused){bPaused=false;SetPause(false);}ToggleMenu();return;}
 if(Id==1009){P->bWeaponWheel=false;UGameplayStatics::SetGlobalTimeDilation(this,1);return;}
 if(bMenu||bPaused)return;
 switch(Id) {
 case 0:P->EnterExit();break;
 case 1:P->Interact();break;
 case 2:if(!P->Vehicle){if(P->GetCharacterMovement()->IsFalling()&&P->GetActorLocation().Z>900)P->ToggleParachute();else P->Vault();}break;
 case 3:P->Cover();break;
 case 4:if(P->bIsCrouched)P->UnCrouch();else P->Crouch();break;
 case 5:P->Reload();break;
 case 6:P->bFirstPerson=!P->bFirstPerson;break;
 case 7:if(P->Vehicle){PMPlay(GetWorld(),TEXT("Horn"),P->GetActorLocation(),.6);if(P->Vehicle->bPolice)P->Vehicle->bSiren=!P->Vehicle->bSiren;}break;
 case 8:if(P->Vehicle)P->Vehicle->bLights=!P->Vehicle->bLights;break;
 case 9:P->bWeaponWheel=true;UGameplayStatics::SetGlobalTimeDilation(this,.25);break;
 case 10:P->ToggleParachute();break;
 case 11:P->Save();break;
 case 12:P->Load();break;
 case 14:bMap=!bMap;bShowMouseCursor=bMap;if(bMap)SetInputMode(FInputModeGameAndUI());else SetInputMode(FInputModeGameOnly());break;
 case 16:if(bMap){float X=0,Y=0;int SX=0,SY=0;GetMousePosition(X,Y);GetViewportSize(SX,SY);float R=FMath::Min(SX*.66f,SY*.77f);
  if(FMath::Abs(X-SX*.5f)<R*.5&&FMath::Abs(Y-SY*.5f)<R*.5){Waypoint=FVector((X-SX*.5f)*430000/R,-(Y-SY*.5f)*430000/R,100);bWaypoint=true;if(auto W=Manager())W->Message(TEXT("Waypoint set | M closes map"));}}else P->Fire();break;
 case 17:case 18: {
  int Next=P->Weapon;for(int n=0;n<PMWeapons().Num();n++){Next=(Next+(Id==17?1:PMWeapons().Num()-1))%PMWeapons().Num();if(P->Owned[Next]){P->Equip(Next);break;}}break;
 }
 default:if(Id>=19&&Id<=27)P->Equip(Id-18);break;
 }
}
void APMController::ToggleMenu() {
 bMap=false;bMenu=!bMenu;bShowMouseCursor=bMenu;
 if(bMenu){FInputModeGameAndUI M;M.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);SetInputMode(M);}
 else SetInputMode(FInputModeGameOnly());
 if(HUDWidget)HUDWidget->RebuildMenu();
}
void APMController::ApplyPreferences() {
 if(auto A=GetWorld()->GetAudioDevice())A->SetTransientPrimaryVolume(SoundVolume);
 if(auto G=UGameUserSettings::GetGameUserSettings()){G->SetOverallScalabilityLevel(GraphicsQuality);G->SetFrameRateLimit(90);G->ApplyNonResolutionSettings();}
}
void APMController::Command(int32 Id) {
 auto P=Player();auto W=Manager();if(!P||!W)return;
 if(Id>=9000&&Id<9004){MenuPage=Id-9000;if(HUDWidget)HUDWidget->RebuildMenu();return;}
 if(Id>=100&&Id<109){W->Teleport(Id-100);ToggleMenu();return;}
 if(Id>=200&&Id<204){W->Weather=Id-200;W->WeatherUpdate();W->Message(TEXT("Weather updated"));return;}
 if(Id>=210&&Id<=213){W->Hour=Id==210?7:Id==211?13:Id==212?18:23;W->WeatherUpdate();return;}
 if(Id>=300&&Id<313) {
  int I=Id-300;const auto& S=PMVehicles()[I];
  FVector Pos=P->GetActorLocation()+P->GetActorForwardVector()*700;Pos.Z+=110;
  if(S.Kind==2) {W->Teleport(3);Pos=FVector(134500,-72500,-60);P->SetActorLocation(Pos+FVector(0,-350,170));P->bSwimming=true;P->GetCharacterMovement()->SetMovementMode(MOVE_Flying);}
  if(S.Kind>=3){W->Teleport(5);Pos=PMLocation(5)+FVector(750,0,40);}
  W->SpawnVehicle(I,Pos,FRotator(0,P->GetActorRotation().Yaw,0));W->Message(S.Name+TEXT(" ready | F to enter"));ToggleMenu();return;
 }
 if(Id>=400&&Id<413){int I=Id-400;P->Owned[I]=true;P->Reserve[I]+=120;P->Ammo[I]=PMWeapons()[I].Magazine;P->Equip(I);W->Message(PMWeapons()[I].Name);return;}
 if(Id>=500&&Id<=505){W->SetWanted(Id-500);W->LastKnown=P->GetActorLocation();return;}
 if(Id>=330&&Id<=335){if(P->Vehicle)P->Vehicle->Customize(Id-330);else W->Message(TEXT("Enter a vehicle first"));return;}
 switch(Id) {
 case 340:if(P->Vehicle){W->Garage.AddUnique(P->Vehicle->Model);P->Save();W->Message(TEXT("Vehicle stored in personal garage"));}break;
 case 341:if(W->Garage.Num())W->SpawnVehicle(W->Garage.Last(),P->GetActorLocation()+FVector(600,0,100));else W->Message(TEXT("Garage is empty"));break;
 case 430:for(int i=0;i<P->Owned.Num();i++){P->Owned[i]=true;P->Reserve[i]=500;P->Ammo[i]=PMWeapons()[i].Magazine;}W->Message(TEXT("All weapons available"));break;
 case 431:for(int& Ammo:P->Reserve)Ammo=500;break;
 case 432:P->Armor=100;P->Health=100;break;
 case 433:P->Cash+=10000;break;
 case 435:P->bInvulnerable=!P->bInvulnerable;W->Message(P->bInvulnerable?TEXT("Invulnerability ON"):TEXT("Invulnerability OFF"));break;
 case 510:W->SpawnHuman(P->GetActorLocation()+FVector(700,0,100),true);break;
 case 600:P->Save();break;
 case 601:P->Load();break;
 case 602:P->Outfit=(P->Outfit+1)%4;P->Variant++;P->Dress(P->Outfit);if(W->Wanted&&!W->bPursuit)W->Unseen+=8;break;
 case 603:P->bSuppressor=!P->bSuppressor;W->Message(P->bSuppressor?TEXT("Suppressor ON"):TEXT("Suppressor OFF"));break;
 case 604:P->bExtended=!P->bExtended;break;
 case 605:P->bGrip=!P->bGrip;break;
 case 606:P->Torch->SetIntensity(P->Torch->Intensity>0?0:12000);break;
 case 607:P->SetActorLocation(P->GetActorLocation()+FVector(0,0,15000));P->GetCharacterMovement()->SetMovementMode(MOVE_Falling);P->ToggleParachute();ToggleMenu();break;
 case 608:P->bScuba=!P->bScuba;P->Breath=100;W->Message(P->bScuba?TEXT("Scuba ON"):TEXT("Scuba OFF"));break;
 case 609:P->Skills.Init(100,7);break;
 case 610:P->Skills.Init(10,7);break;
 case 611:bPaused=!bPaused;SetPause(bPaused);break;
 case 612:W->bTraffic=!W->bTraffic;if(!W->bTraffic)for(auto Car:W->Vehicles)if(IsValid(Car)&&Car->bTraffic&&!Car->Driver)Car->Destroy();break;
 case 613:W->bPedestrians=!W->bPedestrians;if(!W->bPedestrians)for(auto H:W->People)if(IsValid(H)&&!H->bPolice)H->Destroy();break;
 case 614:ConsoleCommand(TEXT("stat fps"));break;
 case 615:W->bFreezeTime=!W->bFreezeTime;break;
 case 616:SoundVolume=FMath::Clamp(SoundVolume-.15f,0.f,1.f);ApplyPreferences();W->Message(FString::Printf(TEXT("Volume %.0f%%"),SoundVolume*100));break;
 case 617:SoundVolume=FMath::Clamp(SoundVolume+.15f,0.f,1.f);ApplyPreferences();W->Message(FString::Printf(TEXT("Volume %.0f%%"),SoundVolume*100));break;
 case 619:Waypoint=FVector(4200,3100,100);bWaypoint=true;ToggleMenu();break;
 case 620:Waypoint=FVector(4200,-4450,100);bWaypoint=true;ToggleMenu();break;
 case 621:Waypoint=FVector(9650,3700,100);bWaypoint=true;ToggleMenu();break;
 case 618:GraphicsQuality=(GraphicsQuality+1)%4;ApplyPreferences();W->Message(FString::Printf(TEXT("Graphics quality %d / 3"),GraphicsQuality));break;
 }
}
void UPMMenuEntry::Click(){if(PC)PC->Command(Id);}
TSharedRef<SWidget> UPMHUD::RebuildWidget() {
 if(!WidgetTree)WidgetTree=NewObject<UWidgetTree>(this);
 RootCanvas=WidgetTree->ConstructWidget<UCanvasPanel>();WidgetTree->RootWidget=RootCanvas;
 MenuBorder=WidgetTree->ConstructWidget<UBorder>();MenuBorder->SetBrushColor(FLinearColor(.015,.027,.039,.97));
 auto MenuSlot=RootCanvas->AddChildToCanvas(MenuBorder);MenuSlot->SetAnchors(FAnchors(.60,.06,.97,.94));MenuSlot->SetOffsets(FMargin(0));
 MenuBorder->SetPadding(FMargin(20));
 auto Scroll=WidgetTree->ConstructWidget<UScrollBox>();MenuBorder->SetContent(Scroll);
 MenuList=WidgetTree->ConstructWidget<UVerticalBox>();Scroll->AddChild(MenuList);
 return Super::RebuildWidget();
}
void UPMHUD::NativeConstruct(){Super::NativeConstruct();RebuildMenu();}
void UPMHUD::RebuildMenu() {
 auto PC=Cast<APMController>(GetOwningPlayer());if(!PC||!MenuBorder)return;
 MenuBorder->SetVisibility(PC->bMenu?ESlateVisibility::Visible:ESlateVisibility::Collapsed);
 if(!PC->bMenu)return;
 MenuList->ClearChildren();Entries.Empty();
 auto Label=[&](FString S,int Size,FLinearColor Color) {
  auto T=WidgetTree->ConstructWidget<UTextBlock>();T->SetText(FText::FromString(S));T->SetColorAndOpacity(Color);T->SetFont(FCoreStyle::GetDefaultFontStyle(TEXT("Regular"),Size));T->SetAutoWrapText(true);
  auto V=MenuList->AddChildToVerticalBox(T);V->SetPadding(FMargin(0,6,0,10));
 };
 auto Button=[&](const FString& S,int Id) {
  auto B=WidgetTree->ConstructWidget<UButton>();B->SetBackgroundColor(FLinearColor(.075,.13,.16));
  auto T=WidgetTree->ConstructWidget<UTextBlock>();T->SetText(FText::FromString(S));T->SetColorAndOpacity(FLinearColor(.85,.91,.92));T->SetFont(FCoreStyle::GetDefaultFontStyle(TEXT("Regular"),13));B->AddChild(T);
  auto V=MenuList->AddChildToVerticalBox(B);V->SetPadding(FMargin(0,2));T->SetMinDesiredWidth(240);
  auto E=NewObject<UPMMenuEntry>(this);E->PC=PC;E->Id=Id;Entries.Add(E);B->OnClicked.AddDynamic(E,&UPMMenuEntry::Click);
 };
 Label(TEXT("PORT MERIDIAN"),22,FLinearColor(.67,.86,.85));
 Label(TEXT("SANDBOX SERVICES   /   F1 closes"),11,FLinearColor(.53,.63,.66));
 Button(TEXT("01  WORLD + WEATHER"),9000);Button(TEXT("02  VEHICLES + GARAGE"),9001);Button(TEXT("03  EQUIPMENT + POLICE"),9002);Button(TEXT("04  PLAYER + SETTINGS"),9003);
 if(PC->MenuPage==0) {
  Label(TEXT("TRAVEL"),13,FLinearColor(.85,.7,.4));
  TArray<FString> Names={TEXT("Downtown"),TEXT("Willow Gardens"),TEXT("Foundry District"),TEXT("Eastport Docks"),TEXT("Solace Coast"),TEXT("Meridian Airfield"),TEXT("North County"),TEXT("Cedar Highlands"),TEXT("West Boulevard")};
  for(int i=0;i<Names.Num();i++)Button(Names[i],100+i);
  Button(TEXT("Route to supply store"),619);Button(TEXT("Route to repair garage"),620);Button(TEXT("Route to safehouse"),621);
  Label(TEXT("ATMOSPHERE"),13,FLinearColor(.85,.7,.4));
  Button(TEXT("Clear"),200);Button(TEXT("Cloud cover"),201);Button(TEXT("Rain"),202);Button(TEXT("Coastal fog"),203);
  Button(TEXT("Sunrise"),210);Button(TEXT("Midday"),211);Button(TEXT("Sunset"),212);Button(TEXT("Night"),213);Button(TEXT("Freeze / resume clock"),615);
 }
 if(PC->MenuPage==1) {
  Label(TEXT("DELIVER VEHICLE"),13,FLinearColor(.85,.7,.4));
  for(int i=0;i<PMVehicles().Num();i++)Button(PMVehicles()[i].Name,300+i);
  Label(TEXT("CURRENT VEHICLE"),13,FLinearColor(.85,.7,.4));
  Button(TEXT("Repair"),330);Button(TEXT("New paint color"),331);Button(TEXT("Engine + brake upgrade"),332);Button(TEXT("Matte finish"),333);Button(TEXT("Gloss finish"),334);Button(TEXT("Spoiler on/off"),335);
  Button(TEXT("Store personal vehicle"),340);Button(TEXT("Retrieve stored vehicle"),341);
 }
 if(PC->MenuPage==2) {
  Label(TEXT("EQUIPMENT"),13,FLinearColor(.85,.7,.4));
  for(int i=0;i<PMWeapons().Num();i++)Button(PMWeapons()[i].Name,400+i);
  Button(TEXT("Unlock all + ammunition"),430);Button(TEXT("Refill ammunition"),431);Button(TEXT("Health + armor"),432);Button(TEXT("Add $10,000"),433);
  Label(TEXT("LAW ENFORCEMENT"),13,FLinearColor(.85,.7,.4));
  for(int i=0;i<=5;i++)Button(FString::Printf(TEXT("Wanted level %d"),i),500+i);
  Button(TEXT("Spawn officer"),510);
 }
 if(PC->MenuPage==3) {
  Button(TEXT("Save free roam [F5]"),600);Button(TEXT("Load free roam [F9]"),601);Button(TEXT("Change clothing / appearance"),602);
  Button(TEXT("Suppressor on/off"),603);Button(TEXT("Extended magazine on/off"),604);Button(TEXT("Stability grip on/off"),605);Button(TEXT("Weapon flashlight"),606);
  Button(TEXT("Parachute jump"),607);Button(TEXT("Scuba + refill breath"),608);Button(TEXT("Max skills"),609);Button(TEXT("Reset skills"),610);
  Button(TEXT("Invulnerability"),435);Button(TEXT("Pause / resume"),611);Button(TEXT("Traffic on/off"),612);Button(TEXT("Pedestrians on/off"),613);Button(TEXT("Show FPS"),614);Button(TEXT("Volume -"),616);Button(TEXT("Volume +"),617);Button(TEXT("Graphics quality: cycle 0-3"),618);
  Label(TEXT("WASD move / Mouse look / Shift sprint\nF vehicle / E shop / Q cover / C crouch\nLMB fire / RMB aim / R reload\nTab + wheel weapons / V camera\nAircraft: Space climb / Ctrl descend"),12,FLinearColor(.66,.72,.74));
 }
}
int32 UPMHUD::NativePaint(const FPaintArgs& Args,const FGeometry& G,const FSlateRect& Cull,FSlateWindowElementList& Out,int32 Layer,const FWidgetStyle& Style,bool Enabled)const {
 const int32 Base=Super::NativePaint(Args,G,Cull,Out,Layer,Style,Enabled);
 auto PC=Cast<APMController>(GetOwningPlayer());if(!PC)return Base;
 auto P=PC->Player();auto W=PC->Manager();if(!P||!W)return Base;
 const FVector2D Size=G.GetLocalSize();const float SW=Size.X,SH=Size.Y;int32 L=Layer+1;
 static FSlateBrush Brush;Brush.DrawAs=ESlateBrushDrawType::Box;Brush.TintColor=FLinearColor::White;
 auto Rect=[&](float X,float Y,float Width,float Height,FLinearColor C) {FSlateDrawElement::MakeBox(Out,L,G.ToPaintGeometry(FVector2D(Width,Height),FSlateLayoutTransform(FVector2D(X,Y))),&Brush,ESlateDrawEffect::None,C);};
 auto Text=[&](const FString& S,float X,float Y,int N,FLinearColor C) {
  FSlateDrawElement::MakeText(Out,L+1,G.ToPaintGeometry(FVector2D(1,1),FSlateLayoutTransform(FVector2D(X,Y))),S,FCoreStyle::GetDefaultFontStyle(TEXT("Regular"),N),ESlateDrawEffect::None,C);
 };
 auto Line=[&](FVector2D A,FVector2D Z,FLinearColor C,float Width) {TArray<FVector2D> Points={A,Z};FSlateDrawElement::MakeLines(Out,L,G.ToPaintGeometry(),Points,ESlateDrawEffect::None,C,true,Width);};
 FLinearColor Teal(.3,.79,.76),White(.88,.93,.94),Muted(.5,.63,.67),Gold(.95,.68,.25);
 Rect(20,16,255,78,FLinearColor(.012,.025,.032,.78));Rect(SW-240,18,220,95,FLinearColor(.012,.025,.032,.78));
 Text(TEXT("PORT MERIDIAN"),32,24,15,White);Text(PMDistrict(P->GetActorLocation()).ToUpper(),32,49,10,Muted);
 Text(FString::Printf(TEXT("%02d:%02d   /   %s"),int(W->Hour),int(FMath::Frac(W->Hour)*60),W->Weather==0?TEXT("CLEAR"):W->Weather==1?TEXT("CLOUDY"):W->Weather==2?TEXT("RAIN"):TEXT("FOG")),32,68,10,Muted);
 Text(FString::Printf(TEXT("$%s"),*FText::AsNumber(P->Cash).ToString()),SW-215,28,19,White);
 FString Stars;for(int i=0;i<5;i++)Stars+=i<W->Wanted?TEXT("* "):TEXT("- ");
 FLinearColor WantedColor=W->Wanted?(W->bPursuit?Gold:(FMath::Sin(W->Clock*5)>0?Gold:Muted)):Muted;
 Text(Stars,SW-215,59,23,WantedColor);
 if(W->Wanted)Text(W->bPursuit?TEXT("ACTIVE PURSUIT"):TEXT("SEARCHING"),SW-215,91,10,WantedColor);
 if(!PC->bMenu)Text(TEXT("F1   SANDBOX SERVICES"),SW-230,SH-31,10,Muted);
 float Radar=200, RX=32, RY=SH-Radar-60, Range=17000;
 if(PC->bMap){Radar=FMath::Min(SW*.66f,SH*.77f);RX=(SW-Radar)*.5;RY=(SH-Radar)*.5;Range=430000;}
 Rect(RX-2,RY-2,Radar+4,Radar+4,FLinearColor(.18,.30,.32,.95));
 Rect(RX,RY,Radar,Radar,FLinearColor(.018,.038,.045,.94));
 FVector Center=PC->bMap?FVector(0,0,0):P->GetActorLocation();
 auto MapPoint=[&](FVector V){return FVector2D(RX+Radar*.5+(V.X-Center.X)/Range*Radar,RY+Radar*.5-(V.Y-Center.Y)/Range*Radar);};
 auto Dot=[&](FVector V,FLinearColor C,float R){auto A=MapPoint(V);if(A.X>RX+3&&A.X<RX+Radar-3&&A.Y>RY+3&&A.Y<RY+Radar-3)Rect(A.X-R,A.Y-R,R*2,R*2,C);};
 for(int i=-9;i<=9;i++) {
  float X=MapPoint(FVector(i*25000,0,0)).X,Y=MapPoint(FVector(0,i*25000,0)).Y;
  if(X>RX&&X<RX+Radar)Rect(X-1,RY,2,Radar,FLinearColor(.13,.21,.23));
  if(Y>RY&&Y<RY+Radar)Rect(RX,Y-1,Radar,2,FLinearColor(.13,.21,.23));
 }
 float Coast=MapPoint(FVector(129000,0,0)).X;
 if(Coast>RX&&Coast<RX+Radar)Rect(Coast,RY,RX+Radar-Coast,Radar,FLinearColor(.025,.16,.21,.8));
 for(auto V:W->Vehicles)if(IsValid(V))Dot(V->GetActorLocation(),V->bPolice?FLinearColor(.4,.6,1):Muted,V->bPolice?3:1.7);
 for(auto H:W->People)if(IsValid(H)&&H->bPolice)Dot(H->GetActorLocation(),FLinearColor(.8,.3,.27),2);
 for(int i=0;i<9;i++)Dot(PMLocation(i),Gold,2.5);
 if(PC->bWaypoint) {
  FVector A=P->GetActorLocation(),B=PC->Waypoint;FVector Road(FMath::RoundToFloat(A.X/25000)*25000,FMath::RoundToFloat(A.Y/25000)*25000,0);FVector EndRoad(FMath::RoundToFloat(B.X/25000)*25000,FMath::RoundToFloat(B.Y/25000)*25000,0);
  TArray<FVector> Route={A,Road,FVector(EndRoad.X,Road.Y,0),EndRoad,B};
  for(int I=0;I<Route.Num()-1;I++){auto U=MapPoint(Route[I]),V=MapPoint(Route[I+1]);U.X=FMath::Clamp(U.X,RX,RX+Radar);U.Y=FMath::Clamp(U.Y,RY,RY+Radar);V.X=FMath::Clamp(V.X,RX,RX+Radar);V.Y=FMath::Clamp(V.Y,RY,RY+Radar);Line(U,V,Gold,2.5);}
  Dot(B,Gold,5);Text(FString::Printf(TEXT("GPS  %.0f m"),FVector::Dist2D(A,B)/100),RX,RY-24,12,Gold);
 }
 if(PC->bMap){Text(TEXT("CLICK: WAYPOINT   /   M: CLOSE"),RX,RY+Radar+15,12,White);for(int i=0;i<9;i++){auto Q=MapPoint(PMLocation(i));Text(PMDistrict(PMLocation(i)),Q.X+5,Q.Y,8,Muted);}}
 Dot(P->GetActorLocation(),Teal,4);
 auto Pos=MapPoint(P->GetActorLocation());float Angle=FMath::DegreesToRadians(P->GetControlRotation().Yaw);
 Line(Pos,Pos+FVector2D(FMath::Cos(Angle),-FMath::Sin(Angle))*13,White,2);
 Text(TEXT("N"),RX+Radar*.5-4,RY+5,9,Muted);
 Rect(32,SH-48,200,5,FLinearColor(.08,.14,.15));Rect(32,SH-48,200*FMath::Clamp(P->Health/100,0.f,1.f),5,Teal);
 Rect(32,SH-39,200,3,FLinearColor(.08,.14,.15));Rect(32,SH-39,200*P->Armor/100,3,FLinearColor(.38,.56,.82));
 if(P->bSwimming){Rect(32,SH-31,200*P->Breath/100,3,FLinearColor(.5,.82,.9));}
 Text(PMWeapons()[P->Weapon].Name.ToUpper(),SW-260,SH-105,12,White);
 Text(P->ReloadTimer>0?TEXT("RELOADING"):FString::Printf(TEXT("%02d  /  %d"),P->Ammo[P->Weapon],P->Reserve[P->Weapon]),SW-260,SH-81,22,White);
 if(P->Vehicle) {
  Text(FString::Printf(TEXT("%03d"),int(FMath::Abs(P->Vehicle->Speed)*.036)),SW*.5-40,SH-100,32,White);
  Text(TEXT("KM/H"),SW*.5-17,SH-56,10,Muted);
  Rect(SW*.5-55,SH-34,110*FMath::Clamp(P->Vehicle->Health/1000,0.f,1.f),3,Teal);
 }
 if(P->bAim&&!PC->bMenu) {
  float X=SW*.5,Y=SH*.5;Line(FVector2D(X-12,Y),FVector2D(X-5,Y),White,1);Line(FVector2D(X+5,Y),FVector2D(X+12,Y),White,1);
  Line(FVector2D(X,Y-12),FVector2D(X,Y-5),White,1);Line(FVector2D(X,Y+5),FVector2D(X,Y+12),White,1);
  if(P->Weapon==8){Line(FVector2D(X-150,Y),FVector2D(X+150,Y),FLinearColor::Black,1);Line(FVector2D(X,Y-150),FVector2D(X,Y+150),FLinearColor::Black,1);}
 }
 if(W->NoticeTime>0&&!PC->bMenu) {Rect(SW*.5-310,SH*.17,620,39,FLinearColor(.015,.03,.04,.83));Text(W->Notice,SW*.5-292,SH*.17+11,12,White);}
 if(P->HurtTimer>0) {Rect(0,0,SW,5,FLinearColor(.8,.04,.025,P->HurtTimer));Rect(0,SH-5,SW,5,FLinearColor(.8,.04,.025,P->HurtTimer));}
 if(P->bDead) {Rect(0,SH*.4,SW,100,FLinearColor(.08,.005,.005,.85));Text(TEXT("CRITICAL CONDITION"),SW*.5-140,SH*.4+30,24,White);}
 if(P->bWeaponWheel) {
  Rect(SW*.5-250,SH*.5-230,500,460,FLinearColor(.01,.025,.03,.92));
  Text(TEXT("EQUIPMENT  /  SCROLL TO SELECT"),SW*.5-175,SH*.5-205,12,Teal);
  for(int i=0;i<PMWeapons().Num();i++) {
   float A=i*2*PI/PMWeapons().Num();float X=SW*.5+FMath::Cos(A)*150-55,Y=SH*.5+FMath::Sin(A)*160;
   Text(PMWeapons()[i].Name,X,Y,10,i==P->Weapon?Gold:P->Owned[i]?White:Muted);
  }
 }
 if(PC->bMenu)Text(FString::Printf(TEXT("X %.0f  Y %.0f  Z %.0f   |   NPC %d   VEH %d"),P->GetActorLocation().X,P->GetActorLocation().Y,P->GetActorLocation().Z,W->People.Num(),W->Vehicles.Num()),32,SH-80,11,White);
 return FMath::Max(Base,L+2);
}
