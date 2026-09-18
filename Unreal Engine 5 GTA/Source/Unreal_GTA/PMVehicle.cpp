#include "PMGame.h"
#include "Engine/DamageEvents.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/AudioComponent.h"
#include "Components/SpotLightComponent.h"
#include "Components/PointLightComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/DamageType.h"

APMVehicle::APMVehicle() {
 PrimaryActorTick.bCanEverTick=true;
 Hull=CreateDefaultSubobject<UBoxComponent>(TEXT("ChaosHull"));RootComponent=Hull;
 Hull->SetBoxExtent(FVector(195,82,42));Hull->SetCollisionProfileName(TEXT("PhysicsActor"));
 Hull->SetNotifyRigidBodyCollision(true);Hull->SetLinearDamping(.08);Hull->SetAngularDamping(2.8);
 Shell=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BlenderBody"));Shell->SetupAttachment(Hull);
 Shell->SetCollisionEnabled(ECollisionEnabled::NoCollision);Shell->SetRelativeLocation(FVector(0,0,-80));
 for(int i=0;i<4;i++) {
  auto W=CreateDefaultSubobject<UStaticMeshComponent>(*FString::Printf(TEXT("Wheel%d"),i));W->SetupAttachment(Hull);W->SetCollisionEnabled(ECollisionEnabled::NoCollision);Wheels.Add(W);
 }
 Rotor=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Rotor"));Rotor->SetupAttachment(Hull);Rotor->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 Spoiler=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("OptionalSpoiler"));Spoiler->SetupAttachment(Hull);Spoiler->SetCollisionEnabled(ECollisionEnabled::NoCollision);Spoiler->SetVisibility(false);
 DriverModel=CreateDefaultSubobject<UPoseableMeshComponent>(TEXT("CivilianDriver"));DriverModel->SetupAttachment(Hull);DriverModel->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 EngineSound=CreateDefaultSubobject<UAudioComponent>(TEXT("EngineAudio"));EngineSound->SetupAttachment(Hull);EngineSound->bAutoActivate=false;
 SirenSound=CreateDefaultSubobject<UAudioComponent>(TEXT("SirenAudio"));SirenSound->SetupAttachment(Hull);SirenSound->bAutoActivate=false;
 Headlights=CreateDefaultSubobject<USpotLightComponent>(TEXT("Headlights"));Headlights->SetupAttachment(Hull);
 Headlights->SetRelativeLocation(FVector(220,0,-10));Headlights->SetIntensity(16000);Headlights->SetAttenuationRadius(7000);Headlights->SetOuterConeAngle(42);
 Headlights->SetCastShadows(false);
 BeaconRed=CreateDefaultSubobject<UPointLightComponent>(TEXT("RedBeacon"));BeaconRed->SetupAttachment(Hull);BeaconRed->SetLightColor(FLinearColor(1,0,0));BeaconRed->SetAttenuationRadius(1600);BeaconRed->SetCastShadows(false);
 BeaconBlue=CreateDefaultSubobject<UPointLightComponent>(TEXT("BlueBeacon"));BeaconBlue->SetupAttachment(Hull);BeaconBlue->SetLightColor(FLinearColor(.01,.14,1));BeaconBlue->SetAttenuationRadius(1600);BeaconBlue->SetCastShadows(false);
}
void APMVehicle::BeginPlay() {
 Super::BeginPlay();WorldManager=Cast<APMWorld>(UGameplayStatics::GetActorOfClass(this,APMWorld::StaticClass()));
 Configure(Model);Hull->OnComponentHit.AddDynamic(this,&APMVehicle::Impact);
}
void APMVehicle::Configure(int32 Index) {
 Model=FMath::Clamp(Index,0,PMVehicles().Num()-1);const auto& S=PMVehicles()[Model];bAircraft=S.Kind>=3;
 Shell->SetStaticMesh(PMMesh(S.Mesh));Shell->SetRelativeLocation(FVector(0,0,-80));
 Hull->SetBoxExtent(FVector(S.Length*(bAircraft?.28:.42),S.Width*(bAircraft?.15:.43),S.Kind==1?42:45));
 Hull->SetMassOverrideInKg(NAME_None,S.Mass,true);Hull->SetCenterOfMass(FVector(0,0,-35));Hull->SetSimulatePhysics(S.Kind<=1);
 Hull->SetEnableGravity(S.Kind<=1);
 if(S.Kind>=2)Shell->SetRelativeLocation(FVector(0,0,S.Kind==2?-30:-70));
 for(int i=0;i<4;i++) {
  Wheels[i]->SetStaticMesh(PMMesh(TEXT("Wheel")));
  Wheels[i]->SetRelativeLocation(FVector((i<2?1:-1)*S.Length*.30,(i%2?1:-1)*(S.Width*.5-5),-44));
  Wheels[i]->SetVisibility(S.Kind<=0);
 }
 if(S.Kind==1) {for(int i=0;i<2;i++){Wheels[i]->SetVisibility(true);Wheels[i]->SetRelativeScale3D(FVector(1,.6,1));Wheels[i]->SetRelativeLocation(FVector(i==0?76:-76,0,-44));}}
 Rotor->SetStaticMesh(PMMesh(S.Kind==3?TEXT("Rotor"):S.Kind==4?TEXT("Propeller"):TEXT("")));
 Rotor->SetRelativeLocation(S.Kind==3?FVector(0,0,205):FVector(345,0,30));Rotor->SetVisibility(bAircraft);
 Spoiler->SetStaticMesh(PMMesh(TEXT("Spoiler")));Spoiler->SetRelativeLocation(FVector(-S.Length*.36,0,45));
 for(int i=0;i<Shell->GetNumMaterials();i++) if(Shell->GetMaterial(i)&&Shell->GetMaterial(i)->GetName().Contains(TEXT("Paint"))) {
  Paint=Shell->CreateDynamicMaterialInstance(i);break;
 }
 Headlights->SetRelativeLocation(FVector(S.Length*.47,0,-5));
 BeaconRed->SetRelativeLocation(FVector(0,-40,85));BeaconBlue->SetRelativeLocation(FVector(0,40,85));
 EngineSound->SetSound(PMSound(S.Kind==3?TEXT("Rotor"):TEXT("Engine")));EngineSound->SetVolumeMultiplier(.12);EngineSound->Play();
 SirenSound->SetSound(PMSound(TEXT("Siren")));SirenSound->SetVolumeMultiplier(.24);
 auto Human=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/GTA/Generated/SK_Citizen.SK_Citizen"));
 if(Human && Human->GetSkeleton())DriverModel->SetSkinnedAssetAndUpdate(Human);
 DriverModel->SetRelativeLocation(FVector(-18,-38,-98));
 for(const auto& Pair:TArray<TPair<FName,float>>{{TEXT("thigh_l"),1.25f},{TEXT("thigh_r"),1.25f},{TEXT("calf_l"),-1.2f},{TEXT("calf_r"),-1.2f},{TEXT("upperarm_l"),1.2f},{TEXT("upperarm_r"),1.2f}}) {
  int B=DriverModel->GetBoneIndex(Pair.Key);if(DriverModel->BoneSpaceTransforms.IsValidIndex(B))DriverModel->BoneSpaceTransforms[B].SetRotation(DriverModel->BoneSpaceTransforms[B].GetRotation()*FQuat(FVector(0,0,1),Pair.Value));
 }
 DriverModel->MarkRefreshTransformDirty();DriverModel->SetRelativeScale3D(FVector(.9));
 DriverModel->SetVisibility(bOccupied);
 bPolice=Model==7||Model==11||bPolice;
}
void APMVehicle::Tick(float Dt) {
 Super::Tick(Dt);
 if(bDestroyed)return;
 DamageTimer-=Dt;AITimer-=Dt;
 if(Driver) {
  auto PC=Cast<APMController>(Driver->GetController());
  if(WorldManager&&WorldManager->bSmokeTest&&WorldManager->SmokeStage==1){Throttle=.8f;Steering=0;bBrake=false;}
  else if(PC&&!PC->bMenu&&!PC->bPaused) {
   Throttle=(PC->IsInputKeyDown(EKeys::W)?1:0)-(PC->IsInputKeyDown(EKeys::S)?1:0);
   Steering=(PC->IsInputKeyDown(EKeys::D)?1:0)-(PC->IsInputKeyDown(EKeys::A)?1:0);
   Lift=(PC->IsInputKeyDown(EKeys::SpaceBar)?1:0)-(PC->IsInputKeyDown(EKeys::LeftControl)?1:0);
   bBrake=PC->IsInputKeyDown(EKeys::SpaceBar)&&!bAircraft;
  }else {Throttle=0;Steering=0;Lift=0;bBrake=true;}
 } else if(bTraffic||bPolice)DriveAI(Dt);else {Throttle=0;Steering=0;Lift=0;bBrake=false;}
 Drive(FMath::Min(Dt,.05f));
 if(Health<250) {
  FireClock+=Dt;
  if(FireClock>.3f&&WorldManager){FireClock=0;WorldManager->Effect(GetActorLocation()+GetActorForwardVector()*100+FVector(0,0,70),2,FLinearColor(.10,.10,.105),1.6);}
  if(Health<80){Health-=Dt*10;if(Health<=0)Explode();}
 }
 Headlights->SetVisibility(bLights&&(Driver||bTraffic||bPolice));
 BeaconRed->SetIntensity(bPolice&&bSiren&&(FMath::Sin(GetWorld()->GetTimeSeconds()*13)>0)?18000:0);
 BeaconBlue->SetIntensity(bPolice&&bSiren&&(FMath::Sin(GetWorld()->GetTimeSeconds()*13)<=0)?18000:0);
 if(bSiren&&bPolice&&!SirenSound->IsPlaying())SirenSound->Play();
 if(!bSiren&&SirenSound->IsPlaying())SirenSound->Stop();
 EngineSound->SetPitchMultiplier(.7f+FMath::Clamp(FMath::Abs(Speed)/4500.f,0.f,1.5f));
 float Distance=WorldManager&&WorldManager->Player?FVector::Dist(GetActorLocation(),WorldManager->Player->GetActorLocation()):0;
 EngineSound->SetVolumeMultiplier(FMath::Clamp(1-Distance/10000.f,0.f,1.f)*(Driver?.19f:.09f));
 SirenSound->SetVolumeMultiplier(FMath::Clamp(1-Distance/18000.f,0.f,1.f)*.22f);
 for(int i=0;i<Wheels.Num();i++)if(Wheels[i]->IsVisible()) {
  Wheels[i]->AddLocalRotation(FRotator(Speed*Dt*1.7,0,0));
  FRotator R=Wheels[i]->GetRelativeRotation();R.Yaw=i<2?Steering*28:0;Wheels[i]->SetRelativeRotation(R);
 }
 RotorPhase+=Dt*(bAircraft?1400:0);
 Rotor->SetRelativeRotation(PMVehicles()[Model].Kind==3?FRotator(0,RotorPhase,0):FRotator(0,0,RotorPhase));
}
void APMVehicle::Drive(float Dt) {
 const auto& S=PMVehicles()[Model];
 if(S.Kind<=1) {
  const FVector V=Hull->GetPhysicsLinearVelocity(),F=GetActorForwardVector(),Right=GetActorRightVector();
  Speed=FVector::DotProduct(V,F);
  int Grounded=0;
  FCollisionQueryParams Q;Q.AddIgnoredActor(this);if(Driver)Q.AddIgnoredActor(Driver);
  for(int i=0;i<4;i++) {
   FVector L((i<2?1:-1)*S.Length*.28,(i%2?1:-1)*S.Width*.36,-10);
   if(S.Kind==1)L.Y=(i%2?1:-1)*19;
   FVector P=GetActorTransform().TransformPosition(L);
   FHitResult H;
   if(GetWorld()->LineTraceSingleByChannel(H,P,P-FVector(0,0,105),ECC_WorldStatic,Q)) {
    Grounded++;
    float Compression=105-H.Distance;
    float Vel=Hull->GetPhysicsLinearVelocityAtPoint(P).Z;
    float Force=FMath::Clamp(Compression*S.Mass*9.8f-Vel*S.Mass*.9f,0.f,S.Mass*980.f);
    Hull->AddForceAtLocation(FVector(0,0,Force),P);
   }
  }
  if(Grounded>=2) {
   float Acc=S.Acceleration*EngineUpgrade*(Health<350?.65f:1.f);
   if(FMath::Abs(Speed)<S.MaxSpeed*EngineUpgrade||Speed*Throttle<0)Hull->AddForce(F*Throttle*Acc*S.Mass);
   float Wet=WorldManager&&WorldManager->Weather>=2?.75f:1;
   Hull->AddForce(-Right*FVector::DotProduct(V,Right)*S.Mass*(bBrake?2.7f:8.5f)*Wet);
   Hull->AddForce(-V*S.Mass*(.045f+(bBrake?4.f*BrakeUpgrade:0.f)+FMath::Abs(Speed)*.000014f));
   FVector AV=Hull->GetPhysicsAngularVelocityInDegrees();
   AV.Z=FMath::FInterpTo(AV.Z,Steering*FMath::Clamp(Speed,-1500.f,4800.f)/S.Length*21.f,Dt,7);
   Hull->SetPhysicsAngularVelocityInDegrees(AV);
   FVector Up=GetActorUpVector();
   Hull->AddTorqueInRadians(FVector::CrossProduct(Up,FVector::UpVector)*S.Mass*(S.Kind==1?400000:110000));
  }
 } else {
  // Water and aircraft use bounded arcade dynamics with swept collision.
  float Target=Throttle*(S.MaxSpeed*EngineUpgrade);
  if(S.Kind==4) {
   Speed=FMath::Clamp(Speed+Throttle*S.Acceleration*Dt-130*Dt,0.f,S.MaxSpeed);
  }else Speed=FMath::FInterpTo(Speed,Target,Dt,S.Kind==2?.65f:1.2f);
  FRotator R=GetActorRotation();
  R.Yaw+=Steering*Dt*(S.Kind==2?32:45);
  FVector P=GetActorLocation();
  if(S.Kind==2) {
   if(P.X<128900)Speed=FMath::Min(Speed,0.f);
   P.Z=-65+FMath::Sin(GetWorld()->GetTimeSeconds()*1.2+P.X*.001)*9;
   R.Pitch=FMath::Sin(GetWorld()->GetTimeSeconds()*1.7)*1.4-Speed*.00045;
   R.Roll=Steering*FMath::Clamp(Speed*.001f,-6.f,6.f);
  } else if(S.Kind==3) {
   P.Z=FMath::Max(100.f,P.Z+Lift*1400*Dt);
   R.Pitch=FMath::FInterpTo(R.Pitch,-Throttle*12,Dt,3);
   R.Roll=FMath::FInterpTo(R.Roll,Steering*15,Dt,3);
  } else {
   float Takeoff=FMath::Clamp((Speed-2300)/3500.f,0.f,1.f);
   P.Z+=((Lift*1700*Takeoff)-FMath::Max(0.f,2300-Speed)*.40f)*Dt;
   P.Z=FMath::Max(100.f,P.Z);
   R.Pitch=FMath::FInterpTo(R.Pitch,Lift*12+Takeoff*3,Dt,2);
   R.Roll=FMath::FInterpTo(R.Roll,Steering*25,Dt,3);
  }
  FHitResult H;SetActorRotation(R);
  FVector Forward=FRotationMatrix(FRotator(0,R.Yaw,0)).GetUnitAxis(EAxis::X);
  FVector Destination=P+Forward*Speed*Dt;
  SetActorLocation(Destination,true,&H);
  if(H.bBlockingHit&&FMath::Abs(Speed)>500){if(WorldManager&&WorldManager->bSmokeTest)UE_LOG(LogTemp,Display,TEXT("PM_FLIGHT_HIT %s point=%s"),*GetNameSafe(H.GetActor()),*H.ImpactPoint.ToString());TakeDamage(FMath::Abs(Speed)*.06,FDamageEvent(),nullptr,this);Speed*=.15f;}
 }
}
void APMVehicle::DriveAI(float Dt) {
 if(!WorldManager||!WorldManager->Player)return;
 FVector P=GetActorLocation();
 const auto& S=PMVehicles()[Model];
 if(bPolice&&WorldManager->Wanted==0){bPolice=false;bTraffic=true;bSiren=false;}
 if(bPolice&&S.Kind==3) {
  FVector Target=WorldManager->bPursuit?WorldManager->Player->GetActorLocation():WorldManager->LastKnown;
  Target+=FVector(2000*FMath::Sin(GetWorld()->GetTimeSeconds()*.15),2000*FMath::Cos(GetWorld()->GetTimeSeconds()*.15),4500);
  FVector D=Target-P;SetActorRotation(FRotator(0,D.Rotation().Yaw,0));
  Throttle=FMath::Clamp(D.Size2D()/5000.f,0.f,.7f);Lift=FMath::Clamp(D.Z/1200.f,-1.f,1.f);Steering=0;bSiren=true;return;
 }
 if(AITarget.IsNearlyZero()||FVector::Dist2D(P,AITarget)<1700) {
  if(bPolice) {
   FVector Target=WorldManager->bPursuit?WorldManager->Player->GetActorLocation():WorldManager->LastKnown;
   if(FVector::Dist2D(P,Target)<6000)AITarget=Target;
   else {
    float GX=FMath::RoundToFloat(P.X/25000)*25000, GY=FMath::RoundToFloat(P.Y/25000)*25000;
    if(FMath::Abs(Target.X-P.X)>FMath::Abs(Target.Y-P.Y))AITarget=FVector(GX+(Target.X>P.X?25000:-25000),GY-400,100);
    else AITarget=FVector(GX+400,GY+(Target.Y>P.Y?25000:-25000),100);
   }
  } else {
   float GX=FMath::FloorToFloat((P.X+1500)/25000)*25000, GY=FMath::FloorToFloat((P.Y+1500)/25000)*25000;
   int Direction=Route%4;
   if(Direction==0)AITarget=FVector(GX+25000,GY-400,100);
   if(Direction==1)AITarget=FVector(GX+400,GY+25000,100);
   if(Direction==2)AITarget=FVector(GX-25000,GY+400,100);
   if(Direction==3)AITarget=FVector(GX-400,GY-25000,100);
   if(FMath::FRand()<.18f)Route=(Route+1)%4;
  }
 }
 FVector D=AITarget-P;
 float Angle=FMath::FindDeltaAngleDegrees(GetActorRotation().Yaw,D.Rotation().Yaw);
 Steering=FMath::Clamp(Angle/32.f,-1.f,1.f);
 Throttle=FMath::Abs(Angle)>65?.28f:bPolice?.90f:.46f;
 bBrake=false;
 FHitResult H;FCollisionQueryParams Q;Q.AddIgnoredActor(this);
 if(GetWorld()->SweepSingleByChannel(H,P,P+GetActorForwardVector()*(650+FMath::Abs(Speed)*.6f),FQuat::Identity,ECC_Pawn,FCollisionShape::MakeSphere(100),Q)) {
  if(H.GetActor()!=WorldManager->Player && H.GetActor()!=WorldManager->Player->Vehicle){Throttle=0;bBrake=true;}
 }
 float Intersection=FMath::Min(FMath::Abs(FMath::Fmod(P.X+250000,25000)),FMath::Abs(FMath::Fmod(P.Y+250000,25000)));
 if(!bPolice&&Intersection<1500 && (int32(GetWorld()->GetTimeSeconds()/8)%2)!=(Route%2)){Throttle=0;bBrake=true;}
 bSiren=bPolice;
 if(bPolice&&FVector::Dist2D(P,WorldManager->Player->GetActorLocation())<1200&&AITimer<=0) {
  AITimer=12;
  auto Officer=WorldManager->SpawnHuman(P+GetActorRightVector()*250,bPolice);if(Officer)Officer->bTactical=WorldManager->Wanted>=4;
 }
}
float APMVehicle::TakeDamage(float Damage,const FDamageEvent& E,AController* I,AActor* C) {
 if(bDestroyed)return 0;
 Health-=Damage;
 if(WorldManager&&C!=this)WorldManager->Crime(bPolice?25:5,GetActorLocation(),4000,bPolice);
 if(Health<=0)Explode();return Damage;
}
void APMVehicle::Impact(UPrimitiveComponent* Hit,AActor* Other,UPrimitiveComponent* Comp,FVector Impulse,const FHitResult& Result) {
 if(bDestroyed||DamageTimer>0)return;
 const float Magnitude=Impulse.Size()/PMVehicles()[Model].Mass;
 if(Magnitude>280) {
  DamageTimer=.4; Health-=Magnitude*.11;
  PMPlay(GetWorld(),TEXT("Impact"),GetActorLocation(),.3);
  if(WorldManager)WorldManager->Effect(Result.ImpactPoint,1,FLinearColor(1,.6,.1),.8);
  if(Driver&&Magnitude>900)UGameplayStatics::ApplyDamage(Driver,Magnitude*.014,nullptr,this,UDamageType::StaticClass());
  if(Health<=0)Explode();
 }
 if(auto Human=Cast<APMHuman>(Other))if(FMath::Abs(Speed)>450) {
  UGameplayStatics::ApplyDamage(Human,FMath::Abs(Speed)*.055,nullptr,Driver?static_cast<AActor*>(Driver):this,UDamageType::StaticClass());
  if(Driver&&WorldManager)WorldManager->Crime(18,GetActorLocation(),7000);
 }
}
void APMVehicle::Repair() {Health=1000;bDestroyed=false;Shell->SetVisibility(true);}
void APMVehicle::Customize(int32 Option) {
 if(Option==0)Repair();
 if(Option==1&&Paint)Paint->SetVectorParameterValue(TEXT("BaseColor"),FLinearColor::MakeRandomColor());
 if(Option==1&&WorldManager&&WorldManager->Wanted&&!WorldManager->bPursuit)WorldManager->Unseen+=6;
 if(Option==2){EngineUpgrade=1.4;BrakeUpgrade=1.4;}
 if(Option==3&&Paint)Paint->SetScalarParameterValue(TEXT("Roughness"),.75);
 if(Option==4&&Paint)Paint->SetScalarParameterValue(TEXT("Roughness"),.19);
 if(Option==5)Spoiler->SetVisibility(!Spoiler->IsVisible());
}
void APMVehicle::Explode() {
 if(bDestroyed)return;
 bDestroyed=true;Health=0;EngineSound->Stop();SirenSound->Stop();
 if(Driver) {auto P=Driver;P->EnterExit();UGameplayStatics::ApplyDamage(P,80,nullptr,this,UDamageType::StaticClass());}
 if(Paint)Paint->SetVectorParameterValue(TEXT("BaseColor"),FLinearColor(.018,.015,.012));
 if(WorldManager){WorldManager->Explosion(GetActorLocation(),1400,120,this);WorldManager->Crime(bPolice?50:30,GetActorLocation(),16000,true);}
}
