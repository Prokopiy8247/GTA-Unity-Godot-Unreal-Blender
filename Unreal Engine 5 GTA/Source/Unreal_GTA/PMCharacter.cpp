#include "PMGame.h"
#include "Engine/DamageEvents.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SpotLightComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Camera/CameraComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "GameFramework/DamageType.h"
#include "Camera/PlayerCameraManager.h"

APMHuman::APMHuman() {
 PrimaryActorTick.bCanEverTick=true;
 GetCapsuleComponent()->InitCapsuleSize(31,90);
 GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
 GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Camera,ECR_Ignore);
 GetCharacterMovement()->MaxWalkSpeed=135;
 GetCharacterMovement()->bOrientRotationToMovement=true;
 GetCharacterMovement()->RotationRate=FRotator(0,420,0);
 GetCharacterMovement()->bRunPhysicsWithNoController=true;
 GetCharacterMovement()->NavAgentProps.bCanCrouch=true;
 GetCharacterMovement()->SetWalkableFloorAngle(48);
 bUseControllerRotationYaw=false;
 GetMesh()->SetVisibility(false);
 Body=CreateDefaultSubobject<UPoseableMeshComponent>(TEXT("AuthoredHuman"));
 Body->SetupAttachment(RootComponent); Body->SetRelativeLocation(FVector(0,0,-90));
 Body->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 Gun=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Weapon"));
 Gun->SetupAttachment(RootComponent); Gun->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 Gun->SetRelativeLocation(FVector(36,20,38)); Gun->SetVisibility(false);
}
void APMHuman::BeginPlay() {
 Super::BeginPlay();
 WorldManager=Cast<APMWorld>(UGameplayStatics::GetActorOfClass(this,APMWorld::StaticClass()));
 Dress(bPolice?(bTactical?3:2):Variant%2);
}
void APMHuman::Dress(int32 Style) {
 FString Name=Style==2?TEXT("Police"):Style==3?TEXT("Tactical"):Style%2==1?TEXT("CitizenF"):TEXT("Citizen");
 USkeletalMesh* M=LoadObject<USkeletalMesh>(nullptr,*(TEXT("/Game/GTA/Generated/SK_")+Name+TEXT(".SK_")+Name));
 if(M && M->GetSkeleton()) { Body->SetSkinnedAssetAndUpdate(M); RestPose=Body->GetBoneSpaceTransforms(); }
 if(!bPolice&&!Cast<APMPlayer>(this)) {
  FRandomStream R(Variant*177+27);
  for(int i=0;i<Body->GetNumMaterials();i++) {
   UMaterialInterface* Mat=Body->GetMaterial(i);
   if(Mat && (Mat->GetName().Contains(TEXT("Fabric"))||Mat->GetName().Contains(TEXT("Jacket")))) {
    auto D=Body->CreateDynamicMaterialInstance(i);
    D->SetVectorParameterValue(TEXT("BaseColor"),FLinearColor(R.FRandRange(.035,.35),R.FRandRange(.04,.28),R.FRandRange(.06,.32)));
   }
  }
 }
 if(bPolice) { Gun->SetStaticMesh(PMMesh(bTactical?TEXT("Rifle"):TEXT("Pistol"))); Gun->SetVisibility(true); }
}
bool APMHuman::CanSee(AActor* Other,float Range) const {
 if(!Other||FVector::DistSquared(GetActorLocation(),Other->GetActorLocation())>FMath::Square(Range))return false;
 FHitResult H; FCollisionQueryParams Q(SCENE_QUERY_STAT(PMHumanVision),false,this);
 bool Hit=GetWorld()->LineTraceSingleByChannel(H,GetActorLocation()+FVector(0,0,60),Other->GetActorLocation()+FVector(0,0,40),ECC_Visibility,Q);
 return !Hit||H.GetActor()==Other||(Cast<APMPlayer>(Other)&&H.GetActor()==Cast<APMPlayer>(Other)->Vehicle);
}
void APMHuman::Animate(float Dt,float Speed,bool Aim,bool Seated) {
 if(RestPose.Num()!=Body->BoneSpaceTransforms.Num())return;
 WalkPhase+=Dt*FMath::Clamp(Speed*.038f,0.f,15.f);
 const float Swing=FMath::Sin(WalkPhase)*FMath::Clamp(Speed/380.f,0.f,1.f)*.6f;
 Body->BoneSpaceTransforms=RestPose;
 auto Rotate=[&](const TCHAR* Name,float Angle) {
  int32 I=Body->GetBoneIndex(Name); if(I!=INDEX_NONE)
   Body->BoneSpaceTransforms[I].SetRotation(RestPose[I].GetRotation()*FQuat(FVector(0,0,1),Angle));
 };
 Rotate(TEXT("thigh_l"),Seated?1.2f:Swing); Rotate(TEXT("thigh_r"),Seated?1.2f:-Swing);
 Rotate(TEXT("calf_l"),Seated?-1.25f:FMath::Max(0.f,-Swing)*.8f); Rotate(TEXT("calf_r"),Seated?-1.25f:FMath::Max(0.f,Swing)*.8f);
 Rotate(TEXT("upperarm_l"),Aim?1.3f:-Swing*.7f); Rotate(TEXT("upperarm_r"),Aim?1.4f:Swing*.7f);
 Rotate(TEXT("forearm_l"),Aim?.35f:.12f); Rotate(TEXT("forearm_r"),Aim?.2f:.12f);
 Body->MarkRefreshTransformDirty();
}
void APMHuman::Tick(float Dt) {
 Super::Tick(Dt);
 if(Cast<APMPlayer>(this))return;
 if(bDead) { DeadTime+=Dt; if(DeadTime>22)Destroy(); return; }
 AI(Dt);bool Aiming=bPolice&&WorldManager&&WorldManager->Wanted>1;Animate(Dt,GetVelocity().Size2D(),Aiming);
 Gun->SetRelativeLocation(Aiming?FVector(36,20,38):FVector(12,27,-7));Gun->SetRelativeRotation(Aiming?FRotator::ZeroRotator:FRotator(-65,0,0));
}
void APMHuman::AI(float Dt) {
 if(!WorldManager||!WorldManager->Player)return;
 auto P=WorldManager->Player;
 Panic=FMath::Max(0.f,Panic-Dt); ShotTimer-=Dt; Think-=Dt;
 if(Think<=0) {
  const float Distance=FVector::Dist(GetActorLocation(),P->GetActorLocation());
  Think=Distance>14000?1.f:.25f;
  if(bPolice && WorldManager->Wanted>0) {
   Target=WorldManager->bPursuit?P->GetActorLocation():WorldManager->LastKnown;
   GetCharacterMovement()->MaxWalkSpeed=WorldManager->Wanted>=3?460:370;
   if(Distance<6500 && CanSee(P,8500)) {
    WorldManager->bPursuit=true; WorldManager->Unseen=0; WorldManager->LastKnown=P->GetActorLocation();
    if(WorldManager->Wanted>=2 && ShotTimer<0 && Distance>190 && !P->bDead) {
     ShotTimer=bTactical?.18f:.7f;
     FVector Start=Gun->GetComponentLocation()+GetActorForwardVector()*45;
     WorldManager->Effect(Start,0,FLinearColor(1,.6,.1),.3);
     PMPlay(GetWorld(),TEXT("Shot"),Start,.15,1.25);
     if(FMath::FRand()<.30f && !P->Vehicle)UGameplayStatics::ApplyDamage(P,bTactical?8:6,nullptr,this,UDamageType::StaticClass());
     else if(P->Vehicle && FMath::FRand()<.45)UGameplayStatics::ApplyDamage(P->Vehicle,12,nullptr,this,UDamageType::StaticClass());
    }
    if(Distance<230 && WorldManager->Wanted==1 && P->Weapon==0 && P->GetVelocity().Size()<120 && !P->Vehicle)P->Respawn(true);
   }
  } else if(Panic>0) {
   FVector Away=(GetActorLocation()-P->GetActorLocation()).GetSafeNormal2D();
   Target=GetActorLocation()+Away*1800; GetCharacterMovement()->MaxWalkSpeed=430;
  } else if(FVector::Dist2D(GetActorLocation(),Target)<130||Target.IsNearlyZero()) {
   FVector Here=GetActorLocation();
   float GX=FMath::RoundToFloat(Here.X/25000)*25000, GY=FMath::RoundToFloat(Here.Y/25000)*25000;
   if(FMath::Abs(Here.X-GX)<FMath::Abs(Here.Y-GY))Target=FVector(GX+(Here.X>GX?1200:-1200),Here.Y+(FMath::RandBool()?1:-1)*FMath::RandRange(1800,6000),Here.Z);
   else Target=FVector(Here.X+(FMath::RandBool()?1:-1)*FMath::RandRange(1800,6000),GY+(Here.Y>GY?1200:-1200),Here.Z);
   GetCharacterMovement()->MaxWalkSpeed=FMath::RandRange(105,170);
  }
 }
 FVector D=(Target-GetActorLocation()).GetSafeNormal2D();
 FHitResult H; FCollisionQueryParams Q;Q.AddIgnoredActor(this);
 if(GetWorld()->LineTraceSingleByChannel(H,GetActorLocation(),GetActorLocation()+D*140,ECC_WorldStatic,Q))D=FVector(-D.Y,D.X,0);
 if(FVector::Dist2D(GetActorLocation(),Target)>100)AddMovementInput(D,1);
 if(bPolice&&P->Vehicle==nullptr&&FVector::Dist2D(GetActorLocation(),P->GetActorLocation())<2400)SetActorRotation((P->GetActorLocation()-GetActorLocation()).Rotation());
}
float APMHuman::TakeDamage(float Damage,const FDamageEvent& Event,AController* DamageInstigator,AActor* Causer) {
 if(bDead)return 0;
 Health-=Damage; Panic=12;
 if(WorldManager && Causer && (Cast<APMPlayer>(Causer)||Cast<APMProjectile>(Causer)))WorldManager->Crime(bPolice?32:12,GetActorLocation(),5000,bPolice);
 if(Health<=0)Die(Causer?(GetActorLocation()-Causer->GetActorLocation()).GetSafeNormal()*30000:FVector::ZeroVector);
 return Damage;
}
void APMHuman::Die(FVector Impulse) {
 bDead=true; Health=0; GetCharacterMovement()->StopMovementImmediately(); GetCharacterMovement()->DisableMovement();
 GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 // Imported skeletal body transfers its current procedural pose to a physics mesh.
 GetMesh()->SetSkeletalMesh(Cast<USkeletalMesh>(Body->GetSkinnedAsset())); GetMesh()->SetRelativeTransform(Body->GetRelativeTransform());
 GetMesh()->SetVisibility(true); Body->SetVisibility(false);
 GetMesh()->SetCollisionProfileName(TEXT("Ragdoll")); GetMesh()->SetSimulatePhysics(true); GetMesh()->AddImpulse(Impulse);
 Gun->SetVisibility(false);
 if(WorldManager) { WorldManager->Crime(bPolice?40:18,GetActorLocation(),4000,bPolice); if(WorldManager->Player)WorldManager->Player->Cash+=FMath::RandRange(5,45); }
}
APMPlayer::APMPlayer() {
 GetCharacterMovement()->MaxWalkSpeed=420; GetCharacterMovement()->JumpZVelocity=590; GetCharacterMovement()->AirControl=.3;
 Boom=CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom")); Boom->SetupAttachment(RootComponent);
 Boom->TargetArmLength=380; Boom->SocketOffset=FVector(0,55,65); Boom->bUsePawnControlRotation=true;
 Boom->bEnableCameraLag=true; Boom->CameraLagSpeed=13; Boom->ProbeSize=14;
 Camera=CreateDefaultSubobject<UCameraComponent>(TEXT("Camera")); Camera->SetupAttachment(Boom);
 Camera->FieldOfView=80;Camera->PostProcessSettings.bOverride_SceneColorTint=true;Camera->PostProcessSettings.SceneColorTint=FLinearColor(.24,.64,.70);Camera->PostProcessBlendWeight=0;
 SuppressorMesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Suppressor"));SuppressorMesh->SetupAttachment(Gun);SuppressorMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 GripMesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Foregrip"));GripMesh->SetupAttachment(Gun);GripMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 MagazineMesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ExtendedMagazine"));MagazineMesh->SetupAttachment(Gun);MagazineMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 Chute=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Parachute")); Chute->SetupAttachment(RootComponent);
 Chute->SetRelativeLocation(FVector(0,0,170)); Chute->SetCollisionEnabled(ECollisionEnabled::NoCollision); Chute->SetVisibility(false);
 Torch=CreateDefaultSubobject<USpotLightComponent>(TEXT("WeaponFlashlight")); Torch->SetupAttachment(Gun); Torch->SetIntensity(0);Torch->SetAttenuationRadius(4500);
 Skills.Init(10,7); Ammo.Init(0,13);Reserve.Init(120,13);Owned.Init(false,13);
 Owned[0]=true; Owned[1]=true;
 for(int i=0;i<PMWeapons().Num();i++)Ammo[i]=PMWeapons()[i].Magazine;
}
void APMPlayer::BeginPlay() {
 Super::BeginPlay();
 Chute->SetStaticMesh(PMMesh(TEXT("Parachute")));SuppressorMesh->SetStaticMesh(PMMesh(TEXT("Suppressor")));GripMesh->SetStaticMesh(PMMesh(TEXT("Foregrip")));MagazineMesh->SetStaticMesh(PMMesh(TEXT("ExtendedMagazine"))); Equip(1);
 if(auto PC=Cast<APlayerController>(GetController())) {
  PC->PlayerCameraManager->ViewPitchMin=-75; PC->PlayerCameraManager->ViewPitchMax=70;
 }
}
void APMPlayer::Tick(float Dt) {
 ACharacter::Tick(Dt);
 if(!WorldManager)WorldManager=Cast<APMWorld>(UGameplayStatics::GetActorOfClass(this,APMWorld::StaticClass()));
 auto PC=Cast<APMController>(GetController());
 FireTimer-=Dt; HurtTimer=FMath::Max(0.f,HurtTimer-Dt);
 if(bDead) {
  RespawnTimer-=Dt; if(RespawnTimer<=0)Respawn(); return;
 }
 if(ReloadTimer>0) {
  ReloadTimer-=Dt;
  if(ReloadTimer<=0) {
   int32 Capacity=PMWeapons()[Weapon].Magazine*(bExtended?2:1);
   int32 Count=FMath::Min(Capacity-Ammo[Weapon],Reserve[Weapon]);
   Ammo[Weapon]+=Count; Reserve[Weapon]-=Count;
  }
 }
 bool Sprint=PC&&PC->IsInputKeyDown(EKeys::LeftShift)&&!bAim&&!bIsCrouched&&Stamina>5;
 Stamina=FMath::Clamp(Stamina+Dt*(Sprint&&GetVelocity().Size2D()>100?-9.f:15.f),0.f,100.f);
 GetCharacterMovement()->MaxWalkSpeed=bInCover?150:bIsCrouched?150:bAim?240:Sprint?680:420;
 if(Sprint&&GetVelocity().Size2D()>100)Skills[0]=FMath::Min(100.f,Skills[0]+Dt*.015f);
 bAim=PC&&!PC->bMenu&&PC->IsInputKeyDown(EKeys::RightMouseButton);
 bUseControllerRotationYaw=bAim&&!Vehicle;
 if(PC&&!PC->bMenu&&!bWeaponWheel&&PC->IsInputKeyDown(EKeys::LeftMouseButton)&&PMWeapons()[Weapon].bAutomatic)Fire();
 if(Vehicle) {
  SetActorLocation(Vehicle->GetActorLocation()+FVector(0,0,65),false,nullptr,ETeleportType::TeleportPhysics);
  Body->SetVisibility(false); Gun->SetVisibility(bAim&&Weapon>0&&Weapon<=3);
  Boom->TargetArmLength=FMath::FInterpTo(Boom->TargetArmLength,bAim?420.f:Vehicle->bAircraft?1250.f:680.f,Dt,5);
  Boom->SocketOffset=FVector(0,bAim?120:0,Vehicle->bAircraft?200:170);
  Skills[Vehicle->bAircraft?5:4]+=Dt*.007;
 } else {
  Boom->TargetArmLength=FMath::FInterpTo(Boom->TargetArmLength,bFirstPerson?0.f:bAim?190.f:380.f,Dt,12);
  Boom->SocketOffset=FVector(bFirstPerson?12:0,bFirstPerson?0:55,bFirstPerson?68:65);
  Body->SetVisibility(!bFirstPerson);
  Gun->SetVisibility(Weapon>0);
  bool InWater=GetActorLocation().X>129000&&GetActorLocation().Z<0;
  if(InWater&&!bSwimming) { bSwimming=true; GetCharacterMovement()->SetMovementMode(MOVE_Flying); }
  if(bSwimming) {
   if(GetActorLocation().X<128800 || GetActorLocation().Z>150) {bSwimming=false;GetCharacterMovement()->SetMovementMode(MOVE_Falling);}
   else {
    float Vertical=PC&&PC->IsInputKeyDown(EKeys::LeftControl)?-1:PC&&PC->IsInputKeyDown(EKeys::SpaceBar)?1:GetActorLocation().Z<-170?.2f:0;
    AddMovementInput(FVector::UpVector,Vertical);
    if(GetActorLocation().Z<-220&&!bScuba)Breath-=Dt*(3.f-Skills[6]*.01f); else Breath=FMath::Min(100.f,Breath+Dt*15);
    if(Breath<=0)TakeDamage(Dt*12,FDamageEvent(),nullptr,this);
    Skills[6]=FMath::Min(100.f,Skills[6]+Dt*.025f);
   }
  }
  if(bParachute) {
   FVector V=GetCharacterMovement()->Velocity; V.Z=FMath::Max(V.Z,-330.f);
   GetCharacterMovement()->Velocity=V;
   if(GetCharacterMovement()->IsMovingOnGround()){bParachute=false;Chute->SetVisibility(false);GetCharacterMovement()->GravityScale=1;}
  }
  Animate(Dt,GetVelocity().Size2D(),bAim,false);
  Gun->SetRelativeLocation(bAim?FVector(43,18,42):FVector(12,27,-7));
  Gun->SetRelativeRotation(bAim?FRotator(GetControlRotation().Pitch,0,0):FRotator(-65,0,0));
 }
 SuppressorMesh->SetVisibility(bSuppressor&&Weapon>=1&&Weapon<=8&&Gun->IsVisible());SuppressorMesh->SetRelativeLocation(FVector(Weapon<3?17:Weapon==3?31:Weapon<7?52:72,0,5));
 GripMesh->SetVisibility(bGrip&&Weapon>=3&&Weapon<=8&&Gun->IsVisible());GripMesh->SetRelativeLocation(FVector(25,0,-3));
 MagazineMesh->SetVisibility(bExtended&&Weapon>=1&&Weapon<=8&&Gun->IsVisible());MagazineMesh->SetRelativeLocation(FVector(Weapon<3?-1:8,0,-8));
 Camera->PostProcessBlendWeight=bSwimming&&GetActorLocation().Z<-220?.8f:0.f;
 float Fov=bAim?(Weapon==8?23.f:Weapon==7?42.f:62.f):80.f;
 Camera->SetFieldOfView(FMath::FInterpTo(Camera->FieldOfView,Fov,Dt,12));
 static float Footstep=0; Footstep-=Dt;
 if(!Vehicle&&GetCharacterMovement()->IsMovingOnGround()&&GetVelocity().Size2D()>80&&Footstep<0) {
  Footstep=Sprint?.27f:.43f; PMPlay(GetWorld(),TEXT("Footstep"),GetActorLocation(),bIsCrouched?.07f:.18f,FMath::FRandRange(.85,1.15));
 }
}
void APMPlayer::Equip(int32 I) {
 if(!PMWeapons().IsValidIndex(I)||!Owned.IsValidIndex(I)||!Owned[I])return;
 Weapon=I;ReloadTimer=0; Gun->SetStaticMesh(PMMesh(PMWeapons()[I].Mesh));Gun->SetVisibility(I>0);
}
void APMPlayer::Fire() {
 if(bDead||FireTimer>0||ReloadTimer>0||!WorldManager)return;
 const auto& W=PMWeapons()[Weapon];
 if(Vehicle&&Weapon>3&&Weapon!=9)return;
 if(W.Magazine>0&&Ammo[Weapon]<=0){Reload();return;}
 FireTimer=W.Interval;
 if(W.Magazine>0)Ammo[Weapon]--;
 FVector Start=Camera->GetComponentLocation(); FVector Dir=Camera->GetForwardVector();
 if(W.Magazine==0) {
  FHitResult H;FCollisionQueryParams Q;Q.AddIgnoredActor(this);
  GetWorld()->SweepSingleByChannel(H,GetActorLocation(),GetActorLocation()+GetActorForwardVector()*W.Range,FQuat::Identity,ECC_Pawn,FCollisionShape::MakeSphere(48),Q);
  if(H.GetActor())UGameplayStatics::ApplyDamage(H.GetActor(),W.Damage+(bIsCrouched?40:0),GetController(),this,UDamageType::StaticClass());
  WorldManager->Effect(GetActorLocation()+GetActorForwardVector()*85+FVector(0,0,10),1,FLinearColor(.5,.45,.35),.22);
  Skills[2]+=.1f;return;
 }
 if(Weapon==9||Weapon==10) {
  auto Proj=GetWorld()->SpawnActor<APMProjectile>(GetActorLocation()+Dir*110+FVector(0,0,50),Dir.Rotation());
  if(Proj){Proj->Source=this;Proj->bRocket=Weapon==10;Proj->Velocity=Dir*(Weapon==10?6500:1250)+FVector(0,0,Weapon==9?320:0);Proj->Fuse=Weapon==10?8:2.8;Proj->Damage=W.Damage;}
 } else {
  for(int i=0;i<W.Pellets;i++) {
   FHitResult H;FCollisionQueryParams Q;Q.AddIgnoredActor(this);if(Vehicle)Q.AddIgnoredActor(Vehicle);
   float Spread=W.Spread*(bAim?.40f:1.f)*(bGrip?.7f:1)*(Vehicle?2.2f:1);
   FVector End=Start+FMath::VRandCone(Dir,Spread)*W.Range;
   if(GetWorld()->LineTraceSingleByChannel(H,Start,End,ECC_Visibility,Q)) {
    End=H.ImpactPoint;
    float Damage=W.Damage;
    if(auto Human=Cast<APMHuman>(H.GetActor()))if(H.ImpactPoint.Z>Human->GetActorLocation().Z+47)Damage*=2.3;
    UGameplayStatics::ApplyPointDamage(H.GetActor(),Damage,Dir,H,GetController(),this,UDamageType::StaticClass());
    WorldManager->Effect(End,1,Cast<APMVehicle>(H.GetActor())?FLinearColor(1,.65,.13):FLinearColor(.38,.32,.25),.35);
   }
  }
 }
 WorldManager->Effect(Gun->GetComponentLocation()+Dir*(Weapon>=4?65:22),0,FLinearColor(1,.7,.18),.3);
 PMPlay(GetWorld(),TEXT("Shot"),GetActorLocation(),bSuppressor?.16f:.60f,Weapon==4?.65:1);
 AddControllerPitchInput(-.30f*(bGrip?.65:1));Skills[1]=FMath::Min(100.f,Skills[1]+.02);
 WorldManager->Crime(Weapon>=9?20:3,GetActorLocation(),bSuppressor?1000:9000);
}
void APMPlayer::Reload() {
 if(Weapon<=0||PMWeapons()[Weapon].Magazine==0||ReloadTimer>0)return;
 if(Ammo[Weapon]>=PMWeapons()[Weapon].Magazine*(bExtended?2:1)||Reserve[Weapon]<=0)return;
 ReloadTimer=Weapon==4?2.2f:1.5f; PMPlay(GetWorld(),TEXT("Reload"),GetActorLocation(),.4);
}
void APMPlayer::EnterExit() {
 if(!WorldManager||bDead)return;
 if(Vehicle) {
  auto V=Vehicle;
  FVector Exit=V->GetActorLocation()+V->GetActorRightVector()*-(PMVehicles()[V->Model].Width*.5+90)+FVector(0,0,80);
  FHitResult H;FCollisionQueryParams Q;Q.AddIgnoredActor(V);Q.AddIgnoredActor(this);
  if(GetWorld()->LineTraceSingleByChannel(H,Exit+FVector(0,0,400),Exit-FVector(0,0,500),ECC_WorldStatic,Q))Exit=H.ImpactPoint+FVector(0,0,100);
  V->Driver=nullptr;V->Throttle=0;V->Steering=0;Vehicle=nullptr;
  SetActorLocation(Exit,false,nullptr,ETeleportType::TeleportPhysics);GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
  GetCharacterMovement()->SetMovementMode(MOVE_Falling);Body->SetVisibility(true);
  return;
 }
 APMVehicle* Closest=nullptr; float Best=450;
 for(auto V:WorldManager->Vehicles) if(IsValid(V)&&!V->bDestroyed&&!V->Driver) {
  float Dist=FVector::Dist(GetActorLocation(),V->GetActorLocation());
  if(Dist<Best){Best=Dist;Closest=V;}
 }
 if(!Closest){WorldManager->Message(TEXT("Move closer to a vehicle [F]"));return;}
 if(Closest->bOccupied) {
  auto Human=WorldManager->SpawnHuman(Closest->GetActorLocation()-Closest->GetActorRightVector()*240);
  if(Human)Human->Panic=15;
  WorldManager->Crime(12,GetActorLocation(),6000,Closest->bPolice);
 }
 if(Closest->bPolice)WorldManager->Crime(40,GetActorLocation(),8000,true);
 Vehicle=Closest; Closest->Driver=this;Closest->bTraffic=false;Closest->bOccupied=false;
 Closest->DriverModel->SetVisibility(false);
 GetCharacterMovement()->StopMovementImmediately();GetCharacterMovement()->DisableMovement();
 GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 bInCover=false;bParachute=false;Chute->SetVisibility(false);
 WorldManager->Message(PMVehicles()[Closest->Model].Name+TEXT(" | WASD drive / Space brake / F exit"));
}
void APMPlayer::Cover() {
 if(Vehicle)return;
 if(bInCover){bInCover=false;UnCrouch();return;}
 FHitResult H;FCollisionQueryParams Q;Q.AddIgnoredActor(this);
 if(GetWorld()->LineTraceSingleByChannel(H,GetActorLocation(),GetActorLocation()+GetActorForwardVector()*140,ECC_WorldStatic,Q)) {
  bInCover=true;CoverNormal=H.ImpactNormal;Crouch();WorldManager->Message(TEXT("Cover | A/D slide, RMB aim, Q leave"));
 }
}
void APMPlayer::Vault() {
 if(Vehicle||bSwimming)return;
 FHitResult Low,High;FCollisionQueryParams Q;Q.AddIgnoredActor(this);
 FVector P=GetActorLocation(), F=GetActorForwardVector()*140;
 if(GetWorld()->LineTraceSingleByChannel(Low,P-FVector(0,0,30),P+F-FVector(0,0,30),ECC_WorldStatic,Q)&&
 !GetWorld()->LineTraceSingleByChannel(High,P+FVector(0,0,80),P+F+FVector(0,0,80),ECC_WorldStatic,Q)) {
  LaunchCharacter(GetActorForwardVector()*500+FVector(0,0,500),true,true);
 }else Jump();
}
void APMPlayer::ToggleParachute() {
 if(Vehicle||GetActorLocation().Z<450)return;
 bParachute=!bParachute;Chute->SetVisibility(bParachute);
 GetCharacterMovement()->GravityScale=bParachute?.15f:1.f;GetCharacterMovement()->AirControl=bParachute?.9f:.3f;
}
void APMPlayer::Landed(const FHitResult& H) {
 float Speed=-GetCharacterMovement()->Velocity.Z; Super::Landed(H);
 if(!bParachute&&Speed>1150)TakeDamage((Speed-1100)*.065f,FDamageEvent(),nullptr,this);
 bParachute=false;Chute->SetVisibility(false);GetCharacterMovement()->GravityScale=1;
}
float APMPlayer::TakeDamage(float Damage,const FDamageEvent& E,AController* I,AActor* C) {
 if(bInvulnerable||bDead)return 0;
 float Absorb=FMath::Min(Armor,Damage*.65f);Armor-=Absorb;Health-=Damage-Absorb;HurtTimer=1;
 if(Health<=0){bDead=true;RespawnTimer=3;if(WorldManager)WorldManager->Message(TEXT("CRITICAL | Returning to medical center"),3);}
 return Damage;
}
void APMPlayer::Respawn(bool Arrest) {
 if(Vehicle)EnterExit();
 bDead=false;Health=100;Armor=Arrest?0:25;Breath=100;Stamina=100;
 Cash=FMath::Max(0,Cash-(Arrest?500:250));bSwimming=false;bParachute=false;bInCover=false;
 GetCharacterMovement()->GravityScale=1;GetCharacterMovement()->SetMovementMode(MOVE_Falling);
 SetActorLocation(PMLocation(0)+FVector(0,1000,50),false,nullptr,ETeleportType::TeleportPhysics);
 Body->SetVisibility(true);if(WorldManager){WorldManager->SetWanted(0);WorldManager->Message(Arrest?TEXT("BUSTED | $500 custody fee"):TEXT("Medical care | $250"));}
}
void APMPlayer::Interact() {
 if(!WorldManager)return;
 FVector P=GetActorLocation();
 if(FVector::Dist2D(P,FVector(9650,3700,0))<1400) { Health=100;Save();WorldManager->Message(TEXT("COVE HOUSE | Free roam saved. F1 > Player for wardrobe."));return;}
 if(Vehicle) {
  FVector GaragePoint(4200,-4450,0);
  if(FVector::Dist2D(P,GaragePoint)<5000) {
   if(Cash>=350){Cash-=350;Vehicle->Repair();WorldManager->Message(TEXT("Foundry Motorworks | repaired for $350"));}
   return;
  }
 }
 // Every generated storefront occupies the first lot inside a 250m city block.
 float LocalX=FMath::Fmod(P.X+2500000,25000),LocalY=FMath::Fmod(P.Y+2500000,25000);
 if(FVector2D::Distance(FVector2D(LocalX,LocalY),FVector2D(4200,3100))<3000) {
  if(Cash>=500) {Cash-=500;Health=100;Armor=100;for(int i=1;i<9;i++){Owned[i]=true;Reserve[i]+=60;}WorldManager->Message(TEXT("MERIDIAN SUPPLY | equipment + health + armor | $500"));}
  else WorldManager->Message(TEXT("Insufficient cash"));
 }else {WorldManager->Message(TEXT("E: supply storefront / repair garage. F: enter vehicle. F1: sandbox services."));}
}
void APMPlayer::Save() {
 auto S=Cast<UPMSave>(UGameplayStatics::CreateSaveGameObject(UPMSave::StaticClass()));
 if(!S)return;
 S->Position=GetActorLocation();if(Vehicle)S->Position+=FVector(0,300,120);
 S->Health=Health;S->Armor=Armor;S->Cash=Cash;S->Weapon=Weapon;S->Outfit=Outfit;S->Ammo=Reserve;S->Magazine=Ammo;S->Skills=Skills;
 for(int i=0;i<Owned.Num();i++)if(Owned[i])S->Owned.Add(i);
 if(WorldManager){S->Hour=WorldManager->Hour;S->Weather=WorldManager->Weather;S->Garage=WorldManager->Garage;}
 S->Suppressor=bSuppressor;S->Extended=bExtended;S->Grip=bGrip;S->Scuba=bScuba;
 if(auto PC=Cast<APMController>(GetController())){S->Volume=PC->SoundVolume;S->Quality=PC->GraphicsQuality;}
 bool Ok=UGameplayStatics::SaveGameToSlot(S,TEXT("PortMeridian"),0);
 if(WorldManager)WorldManager->Message(Ok?TEXT("Free-roam saved"):TEXT("Save failed"));
}
void APMPlayer::Load() {
 auto S=Cast<UPMSave>(UGameplayStatics::LoadGameFromSlot(TEXT("PortMeridian"),0));
 if(!S){if(WorldManager)WorldManager->Message(TEXT("No saved free-roam state yet"));return;}
 if(Vehicle)EnterExit();
 SetActorLocation(S->Position+FVector(0,0,70),false,nullptr,ETeleportType::TeleportPhysics);
 Health=FMath::Max(25.f,S->Health);Armor=S->Armor;Cash=S->Cash;Outfit=S->Outfit;
 if(S->Ammo.Num()==Reserve.Num())Reserve=S->Ammo;
 if(S->Magazine.Num()==Ammo.Num())Ammo=S->Magazine;
 if(S->Skills.Num()==Skills.Num())Skills=S->Skills;
 for(int i:S->Owned)if(Owned.IsValidIndex(i))Owned[i]=true;
 bSuppressor=S->Suppressor;bExtended=S->Extended;bGrip=S->Grip;bScuba=S->Scuba;
 if(auto PC=Cast<APMController>(GetController())){PC->SoundVolume=S->Volume;PC->GraphicsQuality=S->Quality;PC->ApplyPreferences();}
 Equip(S->Weapon);Dress(Outfit);
 if(WorldManager){WorldManager->Hour=S->Hour;WorldManager->Weather=S->Weather;WorldManager->Garage=S->Garage;WorldManager->SetWanted(0);WorldManager->WeatherUpdate();WorldManager->Message(TEXT("Free-roam restored"));}
}
