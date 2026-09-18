#include "PMGame.h"
#include "InputKeyEventArgs.h"
#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Materials/MaterialParameterCollection.h"
#include "Materials/MaterialParameterCollectionInstance.h"
#include "Engine/Engine.h"
#include "HAL/FileManager.h"
#include "Components/StaticMeshComponent.h"
#include "Components/BoxComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Components/AudioComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/CapsuleComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/SkyLight.h"
#include "Components/SkyLightComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "GameFramework/DamageType.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/PlatformMisc.h"
#include "Engine/GameViewportClient.h"

APMEffect::APMEffect() {
 PrimaryActorTick.bCanEverTick=true;RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("EffectRoot"));
 Light=CreateDefaultSubobject<UPointLightComponent>(TEXT("TransientLight"));Light->SetupAttachment(RootComponent);Light->SetCastShadows(false);
}
void APMEffect::Init(int32 Type,FLinearColor Color,float Scale) {
 Kind=Type;Duration=Type==0?.065f:Type==1?.42f:Type==2?2.8f:1.2f;
 const int Count=Type==0?1:Type==1?6:Type==2?4:18;
 Light->SetLightColor(Color);Light->SetIntensity(Type==3?150000:Type==0?6000:0);Light->SetAttenuationRadius(Type==3?2400:380);
 for(int i=0;i<Count;i++) {
  auto M=NewObject<UStaticMeshComponent>(this);M->SetStaticMesh(PMMesh(Type==2?TEXT("Smoke"):TEXT("Spark")));
  M->SetupAttachment(RootComponent);M->RegisterComponent();M->SetCollisionEnabled(ECollisionEnabled::NoCollision);M->SetCastShadow(false);
  M->SetRelativeScale3D(FVector(Scale*(Type==3?4:Type==2?1:.12)));
  if(auto Mat=M->CreateDynamicMaterialInstance(0)){Mat->SetVectorParameterValue(TEXT("BaseColor"),Color);Mat->SetScalarParameterValue(TEXT("Emissive"),Type==2?0:5);}
  Particles.Add(M);Velocities.Add(FMath::VRand()*FMath::FRandRange(60.f,Type==3?700.f:260.f)+FVector(0,0,Type==2?100:30));
 }
 SetLifeSpan(Duration+.1);
}
void APMEffect::Tick(float Dt) {
 Super::Tick(Dt);Life+=Dt;float Alpha=1-Life/Duration;
 for(int i=0;i<Particles.Num();i++) {
  Particles[i]->AddRelativeLocation(Velocities[i]*Dt);
  if(Kind!=2)Velocities[i].Z-=Dt*450;
  if(Kind==2)Particles[i]->SetRelativeScale3D(Particles[i]->GetRelativeScale3D()+FVector(Dt*.7));
  else Particles[i]->SetVisibility(Alpha>0);
 }
 Light->SetIntensity(FMath::Max(0.f,Alpha)*(Kind==3?150000:Kind==0?6000:0));
}
APMProjectile::APMProjectile() {
 PrimaryActorTick.bCanEverTick=true;Mesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Projectile"));RootComponent=Mesh;
 Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}
void APMProjectile::Tick(float Dt) {
 Super::Tick(Dt);
 if(!Mesh->GetStaticMesh())Mesh->SetStaticMesh(PMMesh(bRocket?TEXT("Rocket"):TEXT("Grenade")));
 Fuse-=Dt;if(!bRocket)Velocity.Z-=Dt*650;
 FVector From=GetActorLocation(),To=From+Velocity*Dt;
 FHitResult H;FCollisionQueryParams Q;Q.AddIgnoredActor(this);Q.AddIgnoredActor(Source);
 if(GetWorld()->LineTraceSingleByChannel(H,From,To,ECC_Visibility,Q)) {
  SetActorLocation(H.ImpactPoint+H.ImpactNormal*6);
  if(bRocket){Detonate();return;}
  Velocity=FMath::GetReflectionVector(Velocity,H.ImpactNormal)*.45;
 }else SetActorLocation(To);
 AddActorLocalRotation(FRotator(Dt*140,Dt*75,0));
 if(Fuse<=0)Detonate();
}
void APMProjectile::Detonate() {
 if(auto W=Cast<APMWorld>(UGameplayStatics::GetActorOfClass(this,APMWorld::StaticClass())))W->Explosion(GetActorLocation(),bRocket?1700:1150,Damage,Source);
 Destroy();
}
APMWorld::APMWorld() {
 PrimaryActorTick.bCanEverTick=true;RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("WorldRoot"));
 Rain=CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("RainStreaks"));Rain->SetupAttachment(RootComponent);Rain->SetCollisionEnabled(ECollisionEnabled::NoCollision);Rain->SetCastShadow(false);
 Ambience=CreateDefaultSubobject<UAudioComponent>(TEXT("CityAmbience"));Ambience->SetupAttachment(RootComponent);Ambience->bAutoActivate=false;
 RainAudio=CreateDefaultSubobject<UAudioComponent>(TEXT("RainAmbience"));RainAudio->SetupAttachment(RootComponent);RainAudio->bAutoActivate=false;
 for(int I=0;I<24;I++){auto L=CreateDefaultSubobject<UPointLightComponent>(*FString::Printf(TEXT("StreetPool%d"),I));L->SetupAttachment(RootComponent);L->SetIntensityUnits(ELightUnits::Lumens);L->SetIntensity(0);L->SetAttenuationRadius(2100);L->SetLightColor(FLinearColor(1,.83,.62));L->SetCastShadows(false);StreetLights.Add(L);}
}
void APMWorld::BeginPlay() {
 Super::BeginPlay();
 bSmokeTest=FParse::Param(FCommandLine::Get(),TEXT("PMTest"));
 if(FParse::Param(FCommandLine::Get(),TEXT("PMFlightTest"))){bSmokeTest=true;SmokeStage=12;}
 bCapture=FParse::Param(FCommandLine::Get(),TEXT("PMCapture"));
 if(FParse::Param(FCommandLine::Get(),TEXT("PMUICapture"))){bCapture=true;CaptureStage=13;}
 Rain->SetStaticMesh(PMMesh(TEXT("Spark")));Rain->SetVisibility(false);
 for(int i=0;i<180;i++)Rain->AddInstance(FTransform(FVector::ZeroVector));
 if(auto M=Rain->CreateDynamicMaterialInstance(0)){M->SetVectorParameterValue(TEXT("BaseColor"),FLinearColor(.32,.43,.50));M->SetScalarParameterValue(TEXT("Emissive"),.5);}
 Ambience->SetSound(PMSound(TEXT("City")));Ambience->SetVolumeMultiplier(.16);Ambience->Play();
 RainAudio->SetSound(PMSound(TEXT("Rain")));RainAudio->SetVolumeMultiplier(0);RainAudio->Play();
 Sun=UGameplayStatics::GetActorOfClass(this,ADirectionalLight::StaticClass());
 Fog=UGameplayStatics::GetActorOfClass(this,AExponentialHeightFog::StaticClass());
 Sky=UGameplayStatics::GetActorOfClass(this,ASkyLight::StaticClass());
 WeatherUpdate();
 UE_LOG(LogTemp,Display,TEXT("PM_WORLD_READY: missionless free roam; 13 vehicles; 13 weapon states"));
}
void APMWorld::Message(const FString& Text,float Seconds){Notice=Text;NoticeTime=Seconds;}
bool APMWorld::Visible(FVector From,FVector To,AActor* Ignore)const {
 FHitResult H;FCollisionQueryParams Q;Q.AddIgnoredActor(Ignore);if(Player){Q.AddIgnoredActor(Player);Q.AddIgnoredActor(Player->Vehicle);}
 return !GetWorld()->LineTraceSingleByChannel(H,From,To,ECC_Visibility,Q);
}
void APMWorld::Crime(float Severity,FVector P,float Radius,bool Force) {
 if(!Player)return;
 bool Seen=Force;
 for(auto H:People)if(IsValid(H)&&!H->bDead&&FVector::DistSquared(H->GetActorLocation(),P)<FMath::Square(Radius)) {
  H->Panic=14;
  if(H->CanSee(Player,Radius)) {
   if(H->bPolice)Seen=true;
   else {H->bWitness=true;WitnessTimer=FMath::Max(1.5f,WitnessTimer);Heat+=Severity*.22f;}
  }
 }
 if(Seen){Heat+=Severity;LastKnown=P;Unseen=0;SetWanted(FMath::Clamp(1+int32(Heat/35),1,5));}
 else if(Severity>=20 && Radius>9000) {WitnessTimer=2.5;Heat+=Severity*.5;LastKnown=P;}
}
void APMWorld::SetWanted(int32 Stars) {
 Wanted=FMath::Clamp(Stars,0,5);
 if(Wanted==0){Heat=0;WitnessTimer=0;Unseen=0;bPursuit=false;}
 else {Heat=FMath::Max(Heat,(Wanted-1)*35.f);PoliceTimer=FMath::Min(PoliceTimer,1.f);}
}
void APMWorld::UpdateWanted(float Dt) {
 if(!Player)return;
 if(WitnessTimer>0) {
  WitnessTimer-=Dt;
  if(WitnessTimer<=0) {
   bool Witness=false;
   for(auto H:People)if(IsValid(H)&&!H->bDead&&H->bWitness){Witness=true;H->bWitness=false;}
   if(Witness){SetWanted(FMath::Max(1,1+int32(Heat/35)));LastKnown=Player->GetActorLocation();Message(TEXT("Witness report received | police responding"));}
  }
 }
 if(Wanted<=0)return;
 bPursuit=false;
 for(auto H:People)if(IsValid(H)&&H->bPolice&&!H->bDead&&H->CanSee(Player,Player->bIsCrouched?3800:9000)){bPursuit=true;break;}
 if(!bPursuit)for(auto V:Vehicles)if(IsValid(V)&&V->bPolice&&!V->bDestroyed) {
  float Range=V->bAircraft?19000:14000;
  if(FVector::Dist2D(V->GetActorLocation(),Player->GetActorLocation())<Range&&Visible(V->GetActorLocation()+FVector(0,0,140),Player->GetActorLocation()+FVector(0,0,40),V)){bPursuit=true;break;}
 }
 if(bPursuit){Unseen=0;LastKnown=Player->GetActorLocation();}
 else {
  Unseen+=Dt;
  if(Unseen>14+Wanted*7) {SetWanted(Wanted-1);Heat=FMath::Max(0.f,(Wanted-1)*35.f);Unseen=0;Message(Wanted?TEXT("Search perimeter reduced"):TEXT("Pursuit escaped"));}
 }
 PoliceTimer-=Dt;
 if(PoliceTimer<=0) {
  PoliceTimer=8;
  FVector SearchCenter=bPursuit?Player->GetActorLocation():LastKnown;
  int32 PoliceCount=0,AirCount=0;
  for(auto V:Vehicles)if(IsValid(V)&&V->bPolice&&!V->bDestroyed){PoliceCount++;if(V->bAircraft)AirCount++;}
  if(PoliceCount<Wanted+1) {
   FVector P=(bPursuit?Player->GetActorLocation():LastKnown)-Player->GetActorForwardVector()*(9000+FMath::FRand()*5000);
   P.X=FMath::RoundToFloat(P.X/25000)*25000+400;P.Z=150;
   P.X=FMath::Clamp(P.X,-190000.f,123000.f);
   auto V=SpawnVehicle(7,P,(Player->GetActorLocation()-P).Rotation(),false,true);
   if(V){V->bOccupied=true;V->bSiren=true;}
  }
  int32 OfficerCount=0;for(auto H:People)if(IsValid(H)&&H->bPolice&&!H->bDead)OfficerCount++;
  if(OfficerCount<FMath::Min(8,Wanted*2)) {
   FVector P=SearchCenter-Player->GetActorForwardVector()*FMath::RandRange(2500,4500);
   P.Z=150;auto H=SpawnHuman(P,true);if(H&&Wanted>=4){H->bTactical=true;H->Dress(3);}
  }
  if(Wanted>=3&&AirCount==0) {
   FVector P=SearchCenter+FVector(-14000,5000,6500);
   SpawnVehicle(11,P,FRotator::ZeroRotator,false,true);
  }
  if(Wanted>=3&&PoliceCount<Wanted+3&&FMath::FRand()<.3) {
   FVector P=SearchCenter+Player->GetActorForwardVector()*10000;
   P.X=FMath::RoundToFloat(P.X/25000)*25000;P.Z=150;
   SpawnVehicle(7,P,FRotator(0,90,0),false,true);
  }
 }
}
APMVehicle* APMWorld::SpawnVehicle(int32 Index,FVector P,FRotator R,bool Traffic,bool Police) {
 FTransform T(R,P);
 auto V=GetWorld()->SpawnActorDeferred<APMVehicle>(APMVehicle::StaticClass(),T,nullptr,nullptr,ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
 if(V){V->Model=Index;V->bTraffic=Traffic;V->bPolice=Police;V->bOccupied=Traffic||Police;UGameplayStatics::FinishSpawningActor(V,T);Vehicles.Add(V);}
 return V;
}
APMHuman* APMWorld::SpawnHuman(FVector P,bool Police) {
 FHitResult H;FCollisionQueryParams Q;
 if(GetWorld()->LineTraceSingleByChannel(H,P+FVector(0,0,500),P-FVector(0,0,1000),ECC_WorldStatic,Q))P.Z=H.ImpactPoint.Z+95;
 FTransform T(FRotator(0,FMath::FRand()*360,0),P);
 auto A=GetWorld()->SpawnActorDeferred<APMHuman>(APMHuman::StaticClass(),T,nullptr,nullptr,ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn);
 if(A){A->bPolice=Police;A->Variant=FMath::RandRange(0,99);UGameplayStatics::FinishSpawningActor(A,T);People.Add(A);}
 return A;
}
void APMWorld::Populate() {
 if(!Player)return;
 FVector P=Player->GetActorLocation();
 People.RemoveAll([](auto H){return !IsValid(H);});Vehicles.RemoveAll([](auto V){return !IsValid(V);});
 for(auto H:People)if(IsValid(H)&&FVector::DistSquared(P,H->GetActorLocation())>FMath::Square(24000.f))H->Destroy();
 for(auto V:Vehicles)if(IsValid(V)&&!V->Driver&&(V->bTraffic||V->bPolice)&&FVector::DistSquared(P,V->GetActorLocation())>FMath::Square(45000.f))V->Destroy();
 bool Urban=P.X>-100000&&P.X<129000&&P.Y<125000;
 if(bPedestrians&&Urban)for(int n=0;n<4&&People.Num()<40;n++) {
  FVector Pos=P+FVector(FMath::FRandRange(-11000.f,11000.f),FMath::FRandRange(-11000.f,11000.f),0);
  if(FMath::RandBool())Pos.X=FMath::RoundToFloat(Pos.X/25000)*25000+(FMath::RandBool()?1200:-1200);
  else Pos.Y=FMath::RoundToFloat(Pos.Y/25000)*25000+(FMath::RandBool()?1200:-1200);
  Pos.Z=170;if(FVector::Dist2D(P,Pos)>1500)SpawnHuman(Pos);
 }
 int32 TrafficCount=0;for(auto V:Vehicles)if(IsValid(V)&&V->bTraffic)TrafficCount++;
 if(bTraffic&&Urban)for(int n=0;n<2&&TrafficCount<22;n++,TrafficCount++) {
  FVector Pos=P+FVector(FMath::FRandRange(-18000.f,18000.f),FMath::FRandRange(-18000.f,18000.f),0);
  int32 Route=FMath::RandRange(0,3);
  if(Route%2==0)Pos.Y=FMath::RoundToFloat(Pos.Y/25000)*25000+(Route==0?-400:400);
  else Pos.X=FMath::RoundToFloat(Pos.X/25000)*25000+(Route==1?400:-400);
  Pos.Z=160;
  if(FVector::Dist2D(P,Pos)>2800)if(auto V=SpawnVehicle(FMath::RandRange(0,6),Pos,FRotator(0,Route*90,0),true))V->Route=Route;
 }
}
void APMWorld::Tick(float Dt) {
 Super::Tick(Dt);Clock+=Dt;NoticeTime=FMath::Max(0.f,NoticeTime-Dt);
 if(!Player)Player=Cast<APMPlayer>(UGameplayStatics::GetPlayerCharacter(this,0));
 if(!Player)return;
 Player->WorldManager=this;
 if(!bFreezeTime)Hour=FMath::Fmod(Hour+Dt/90,24.f);
 PopulationTimer-=Dt;WeatherTimer-=Dt;
 if(PopulationTimer<=0){PopulationTimer=1.5;Populate();}
 if(WeatherTimer<=0){WeatherTimer=2;WeatherUpdate();}
 UpdateWanted(Dt);
 if(Player->GetActorLocation().Z<-18000)Player->Respawn();
 if(bSmokeTest)SmokeTest(Dt);
 if(bCapture)Capture(Dt);
 Rain->SetVisibility(Weather==2);
 if(Weather==2) {
  FVector P=Player->GetActorLocation();
  for(int i=0;i<180;i++) {
   float X=FMath::Sin(i*7.51f)*1400,Y=FMath::Cos(i*9.93f)*1400,Z=FMath::Fmod(i*97.f+Clock*1500.f,1600.f);
   Rain->UpdateInstanceTransform(i,FTransform(FRotator(8,0,0),P+FVector(X,Y,1100-Z),FVector(.025,.025,3.5)),true,i==179,true);
  }
 }
}
void APMWorld::WeatherUpdate() {
 if(auto MPC=LoadObject<UMaterialParameterCollection>(nullptr,TEXT("/Game/GTA/Materials/MPC_Weather.MPC_Weather")))
  GetWorld()->GetParameterCollectionInstance(MPC)->SetScalarParameterValue(TEXT("Wetness"),Weather==2?.8f:0.f);
 if(RainAudio)RainAudio->SetVolumeMultiplier(Weather==2?.28f:0.f);
 if(auto S=Cast<ADirectionalLight>(Sun)) {
  float Angle=(Hour-6)/24*360;
  S->SetActorRotation(FRotator(-FMath::Sin(FMath::DegreesToRadians(Angle))*70,Hour*15-90,0));
  auto L=Cast<UDirectionalLightComponent>(S->GetLightComponent());
  const float Day=FMath::Clamp(FMath::Sin(FMath::DegreesToRadians(Angle)),0.f,1.f);
  L->SetIntensity(Day*(Weather==0?65000.f:Weather==1?40000.f:18000.f)+.65f);
  if(Day<=0)S->SetActorRotation(FRotator(-28,Hour*15,0));
  L->SetLightColor(Day<=0?FLinearColor(.24,.36,.65):Day<.35?FLinearColor(1,.72,.48):FLinearColor(1,.97,.90));
 }
 if(auto F=Cast<AExponentialHeightFog>(Fog)) {
  auto C=F->GetComponent();C->SetFogDensity(Weather==3?.028:Weather==2?.009:.0025);
  C->SetFogInscatteringColor(Weather==3?FLinearColor(.40,.46,.5):FLinearColor(.51,.64,.73));
 }
 if(auto S=Cast<ASkyLight>(Sky))S->GetLightComponent()->SetIntensity(Hour>6&&Hour<19?1.25:.6);
 if(Player){TArray<FVector> Points;FVector P=Player->GetActorLocation();int GX=FMath::FloorToInt(P.X/25000),GY=FMath::FloorToInt(P.Y/25000);
 for(int X=GX-1;X<=GX+1;X++)for(int Y=GY-1;Y<=GY+1;Y++)for(int I=0;I<5;I++){Points.Add(FVector(X*25000+1800+I*5000,Y*25000+1090,620));Points.Add(FVector(X*25000+1090,Y*25000+1800+I*5000,620));}
 Points.Sort([&](const FVector& A,const FVector& B){return FVector::DistSquared(A,P)<FVector::DistSquared(B,P);});
 for(int I=0;I<StreetLights.Num();I++){StreetLights[I]->SetWorldLocation(Points[I]);StreetLights[I]->SetIntensity((Hour<7||Hour>18)&&P.X<125000&&P.X>-100000&&P.Y<125000?3600:0);}}
}
void APMWorld::Teleport(int32 District) {
 if(!Player)return;if(Player->Vehicle)Player->EnterExit();
 Player->SetActorLocation(PMLocation(District),false,nullptr,ETeleportType::TeleportPhysics);
 Player->GetCharacterMovement()->StopMovementImmediately();Player->GetCharacterMovement()->SetMovementMode(MOVE_Falling);
 Message(PMDistrict(PMLocation(District)));
}
void APMWorld::Effect(FVector P,int32 Type,FLinearColor Color,float Scale) {
 if(auto E=GetWorld()->SpawnActor<APMEffect>(P,FRotator::ZeroRotator))E->Init(Type,Color,Scale);
}
void APMWorld::Explosion(FVector P,float Radius,float Damage,AActor* Source) {
 Effect(P,3,FLinearColor(1,.20,.015),3);Effect(P+FVector(0,0,100),2,FLinearColor(.08,.075,.07),5);
 PMPlay(GetWorld(),TEXT("Explosion"),P,.85);
 auto Apply=[&](AActor* A) {if(!IsValid(A)||A==Source)return;float D=FVector::Dist(P,A->GetActorLocation());if(D<Radius)UGameplayStatics::ApplyDamage(A,Damage*(1-D/Radius),nullptr,Source,UDamageType::StaticClass());};
 Apply(Player);for(auto H:People)Apply(H);
 TArray<TObjectPtr<APMVehicle>> Copy=Vehicles;
 for(auto V:Copy)if(IsValid(V)) {Apply(V);if(V->Hull->IsSimulatingPhysics())V->Hull->AddRadialImpulse(P,Radius,1200,ERadialImpulseFalloff::RIF_Linear,true);}
 Crime(25,P,15000,true);
}
void APMWorld::SmokeTest(float Dt) {
 SmokeTimer+=Dt;
 if(SmokeStage==12&&SmokeTimer<.1)Teleport(5);
 if(SmokeStage==0) {
  if(SmokeTimer<.5f)TestStart=Player->GetActorLocation();
  if(auto PC=Cast<APlayerController>(Player->GetController())) {
   if(SmokeTimer>1&&SmokeTimer<4)PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::W,IE_Pressed,1.f));
   else if(SmokeTimer>=4)PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::W,IE_Released,0.f));
  }
  if(SmokeTimer>6) {
   bool Assets=Player->Body->GetSkinnedAsset()!=nullptr&&PMMesh(TEXT("Sedan"))&&PMMesh(TEXT("Office"))&&PMMesh(TEXT("Pistol"));
   UE_LOG(LogTemp,Display,TEXT("PM_TEST_ASSETS=%s"),Assets?TEXT("PASS"):TEXT("FAIL"));
   UE_LOG(LogTemp,Display,TEXT("PM_TEST_WALK=%s distance=%.0f"),FVector::Dist2D(TestStart,Player->GetActorLocation())>150?TEXT("PASS"):TEXT("FAIL"),FVector::Dist2D(TestStart,Player->GetActorLocation()));
   for(int i=0;i<PMVehicles().Num();i++) {
    auto V=SpawnVehicle(i,FVector(4000+(i%5)*1100,-6500-(i/5)*1600,150));
    UE_LOG(LogTemp,Display,TEXT("PM_TEST_VEHICLE_%d=%s"),i,V&&V->Shell->GetStaticMesh()?TEXT("PASS"):TEXT("FAIL"));
   }
   TestCar=SpawnVehicle(1,FVector(0,-3500,160),FRotator(0,90,0));
   Player->SetActorLocation(FVector(-260,-3500,170));Player->EnterExit();TestStart=TestCar->GetActorLocation();
   UE_LOG(LogTemp,Display,TEXT("PM_TEST_ENTER=%s"),Player->Vehicle==TestCar?TEXT("PASS"):TEXT("FAIL"));
   SmokeStage=1;SmokeTimer=0;
  }
 }
 else if(SmokeStage==1&&SmokeTimer>6) {
  float Distance=FVector::Dist2D(TestStart,TestCar->GetActorLocation());
  UE_LOG(LogTemp,Display,TEXT("PM_TEST_DRIVE=%s distance=%.0f speed=%.0f"),Distance>250?TEXT("PASS"):TEXT("FAIL"),Distance,TestCar->Speed);
  Player->EnterExit();UE_LOG(LogTemp,Display,TEXT("PM_TEST_EXIT=%s"),!Player->Vehicle?TEXT("PASS"):TEXT("FAIL"));
  bTraffic=false;bPedestrians=false;
  for(auto H:People)if(IsValid(H))H->Destroy();
  for(auto V:Vehicles)if(IsValid(V)&&FVector::Dist2D(V->GetActorLocation(),FVector(0,-1200,0))<4000)V->Destroy();
  Player->SetActorLocation(FVector(0,-1200,150));Player->GetCharacterMovement()->SetMovementMode(MOVE_Falling);
  if(auto PC=Cast<APMController>(Player->GetController()))PC->SetControlRotation(FRotator(0,0,0));
  TestTarget=SpawnHuman(FVector(650,-1145,150));TestTarget->GetCharacterMovement()->MaxWalkSpeed=0;TestTarget->Target=TestTarget->GetActorLocation();TestTarget->Think=100;
  Player->Equip(1);SmokeStage=2;SmokeTimer=0;
 }
 else if(SmokeStage==2) {
  if(auto PC=Cast<APMController>(Player->GetController()))PC->SetControlRotation((TestTarget->GetActorLocation()+FVector(0,0,30)-Player->Camera->GetComponentLocation()).Rotation());
  if(SmokeTimer>2.0){Player->Fire();SmokeStage=3;SmokeTimer=0;}
 }
 else if(SmokeStage==3&&SmokeTimer>2) {
  UE_LOG(LogTemp,Display,TEXT("PM_TEST_HITSCAN=%s health=%.1f"),TestTarget&&TestTarget->Health<100?TEXT("PASS"):TEXT("FAIL"),TestTarget?TestTarget->Health:0);
  if(TestTarget){UGameplayStatics::ApplyDamage(TestTarget,150,nullptr,Player,UDamageType::StaticClass());UE_LOG(LogTemp,Display,TEXT("PM_TEST_DAMAGE=%s"),TestTarget->bDead?TEXT("PASS"):TEXT("FAIL"));}
  Player->Save();Player->Cash=1;Player->Load();UE_LOG(LogTemp,Display,TEXT("PM_TEST_SAVE=%s"),Player->Cash>1?TEXT("PASS"):TEXT("FAIL"));
  bTraffic=true;bPedestrians=true;SetWanted(3);LastKnown=Player->GetActorLocation();SmokeStage=4;SmokeTimer=0;
 }
 else if(SmokeStage==4&&SmokeTimer>10) {
  int Officers=0,Cars=0,Air=0;
  for(auto H:People)if(IsValid(H)&&H->bPolice)Officers++;
  for(auto V:Vehicles)if(IsValid(V)&&V->bPolice){Cars++;if(V->bAircraft)Air++;}
  UE_LOG(LogTemp,Display,TEXT("PM_TEST_POLICE=%s officers=%d vehicles=%d air=%d"),Officers>0&&Cars>0&&Air>0?TEXT("PASS"):TEXT("FAIL"),Officers,Cars,Air);
  UE_LOG(LogTemp,Display,TEXT("PM_TEST_POPULATION: people=%d vehicles=%d wanted=%d"),People.Num(),Vehicles.Num(),Wanted);

  Player->bInvulnerable=true;SetWanted(0);
  for(auto H:People)if(IsValid(H)&&H->bPolice)H->Destroy();
  for(auto V:Vehicles)if(IsValid(V)&&V->bPolice)V->Destroy();
  if(auto PC=Cast<APMController>(Player->GetController())) {
   PC->ToggleMenu();
   UE_LOG(LogTemp,Display,TEXT("PM_TEST_UMG=%s buttons=%d"),PC->HUDWidget&&PC->HUDWidget->Entries.Num()>12?TEXT("PASS"):TEXT("FAIL"),PC->HUDWidget?PC->HUDWidget->Entries.Num():0);
   PC->ToggleMenu();
  }
  Teleport(5);SmokeStage=5;SmokeTimer=0;
 }
 else if(SmokeStage==5&&SmokeTimer>4) {
  TestCar=SpawnVehicle(10,FVector(-174000,-87000,500));Player->SetActorLocation(TestCar->GetActorLocation()+FVector(0,-280,0));Player->EnterExit();
  TestStart=TestCar->GetActorLocation();SmokeStage=6;SmokeTimer=0;
 }
 else if(SmokeStage==6) {
  if(auto PC=Cast<APMController>(Player->GetController())) {
   PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::W,IE_Pressed,1.f));PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::SpaceBar,IE_Pressed,1.f));
   if(SmokeTimer>6) {
    PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::W,IE_Released,0.f));PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::SpaceBar,IE_Released,0.f));
    FVector Travel=TestCar->GetActorLocation()-TestStart;
    UE_LOG(LogTemp,Display,TEXT("PM_TEST_HELICOPTER=%s travel=%.0f climb=%.0f"),Travel.Size2D()>1000&&Travel.Z>1000?TEXT("PASS"):TEXT("FAIL"),Travel.Size2D(),Travel.Z);
    Player->EnterExit();Teleport(3);SmokeStage=7;SmokeTimer=0;
   }
  }
 }
 else if(SmokeStage==7&&SmokeTimer>4) {
  TestCar=SpawnVehicle(9,FVector(134500,-72500,-65));Player->SetActorLocation(TestCar->GetActorLocation()+FVector(0,-220,40));Player->EnterExit();
  TestStart=TestCar->GetActorLocation();SmokeStage=8;SmokeTimer=0;
 }
 else if(SmokeStage==8) {
  if(auto PC=Cast<APMController>(Player->GetController())) {
   PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::W,IE_Pressed,1.f));
   if(SmokeTimer>5) {
    PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::W,IE_Released,0.f));
    FVector Travel=TestCar->GetActorLocation()-TestStart;
    UE_LOG(LogTemp,Display,TEXT("PM_TEST_BOAT=%s travel=%.0f z=%.0f"),Travel.Size2D()>1000&&FMath::Abs(Travel.Z)<100?TEXT("PASS"):TEXT("FAIL"),Travel.Size2D(),Travel.Z);
    Player->EnterExit();Player->SetActorLocation(FVector(135000,-74000,-400));Player->Breath=100;Player->bScuba=false;
    SmokeStage=9;SmokeTimer=0;
   }
  }
 }
 else if(SmokeStage==9) {
  if(auto PC=Cast<APMController>(Player->GetController()))PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::LeftControl,IE_Pressed,1.f));
  if(SmokeTimer<=2)return;
  if(auto PC=Cast<APMController>(Player->GetController()))PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::LeftControl,IE_Released,0.f));
  UE_LOG(LogTemp,Display,TEXT("PM_TEST_SWIM=%s breath=%.1f"),Player->bSwimming&&Player->Breath<100?TEXT("PASS"):TEXT("FAIL"),Player->Breath);
  if(auto PC=Cast<APMController>(Player->GetController())){PC->Command(607);if(PC->bMenu)PC->ToggleMenu();}
  SmokeStage=10;SmokeTimer=0;
 }
 else if(SmokeStage==10&&SmokeTimer>2) {
  UE_LOG(LogTemp,Display,TEXT("PM_TEST_PARACHUTE=%s vz=%.0f"),Player->bParachute&&Player->GetVelocity().Z>=-345?TEXT("PASS"):TEXT("FAIL"),Player->GetVelocity().Z);
  Player->bParachute=false;Player->Chute->SetVisibility(false);Player->GetCharacterMovement()->GravityScale=1;
  Teleport(0);
  for(auto H:People)if(IsValid(H)&&H->bPolice)H->Destroy();
  for(auto V:Vehicles)if(IsValid(V)&&V->bPolice)V->Destroy();
  SetWanted(2);PoliceTimer=1000;WitnessTimer=0;Unseen=60;UpdateWanted(.01f);Unseen=60;UpdateWanted(.01f);
  UE_LOG(LogTemp,Display,TEXT("PM_TEST_ESCAPE=%s wanted=%d"),Wanted==0?TEXT("PASS"):TEXT("FAIL"),Wanted);
  SmokeStage=11;SmokeTimer=0;
 }
 else if(SmokeStage==11&&SmokeTimer>4) {
  Player->SetActorLocation(FVector(4200,3100,160));Player->Cash=2000;Player->Interact();
  UE_LOG(LogTemp,Display,TEXT("PM_TEST_SHOP=%s cash=%d"),Player->Cash==1500&&Player->Armor==100&&Player->Owned[8]?TEXT("PASS"):TEXT("FAIL"),Player->Cash);
  TestCar=SpawnVehicle(2,FVector(4200,2000,180));TestCar->Health=90;TestCar->Customize(0);TestCar->Customize(2);
  UE_LOG(LogTemp,Display,TEXT("PM_TEST_GARAGE=%s"),TestCar->Health==1000&&TestCar->EngineUpgrade>1?TEXT("PASS"):TEXT("FAIL"));
  Teleport(5);SmokeStage=12;SmokeTimer=0;
 }
 else if(SmokeStage==12&&SmokeTimer>4) {
  TestCar=SpawnVehicle(12,FVector(-190000,-87500,120));Player->SetActorLocation(TestCar->GetActorLocation()+FVector(0,-250,50));Player->EnterExit();TestStart=TestCar->GetActorLocation();UE_LOG(LogTemp,Display,TEXT("PM_PLANE_ENTER driver=%d playerVehicle=%d"),TestCar->Driver!=nullptr,Player->Vehicle==TestCar);SmokeStage=13;SmokeTimer=0;
 }
 else if(SmokeStage==13) {
  if(auto PC=Cast<APMController>(Player->GetController())) {
   PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::LeftControl,IE_Released,0.f));
   PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::W,IE_Pressed,1.f));PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::SpaceBar,IE_Pressed,1.f));
   if(FMath::FloorToInt(SmokeTimer)!=FMath::FloorToInt(SmokeTimer-Dt))UE_LOG(LogTemp,Display,TEXT("PM_PLANE_STATE time=%.0f throttle=%.2f lift=%.2f speed=%.0f health=%.0f z=%.0f"),SmokeTimer,TestCar->Throttle,TestCar->Lift,TestCar->Speed,TestCar->Health,TestCar->GetActorLocation().Z);
   if(SmokeTimer>8){
    PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::W,IE_Released,0.f));PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::SpaceBar,IE_Released,0.f));
    FVector Travel=TestCar->GetActorLocation()-TestStart;
    UE_LOG(LogTemp,Display,TEXT("PM_TEST_AIRPLANE=%s travel=%.0f climb=%.0f"),Travel.Size2D()>2000&&Travel.Z>1000?TEXT("PASS"):TEXT("FAIL"),Travel.Size2D(),Travel.Z);
    UE_LOG(LogTemp,Display,TEXT("PM_SMOKE_COMPLETE"));
    FFileHelper::SaveStringToFile(TEXT("Runtime smoke completed; inspect PM_TEST entries for per-feature PASS/FAIL.\n"),*(FPaths::ProjectSavedDir()/TEXT("PM_SmokeComplete.txt")));
    PC->ConsoleCommand(TEXT("quit"));SmokeStage=14;
   }
  }
 }

}
APMGameMode::APMGameMode() {DefaultPawnClass=APMPlayer::StaticClass();PlayerControllerClass=APMController::StaticClass();}
void APMGameMode::StartPlay() {
 Super::StartPlay();
 if(auto P=UGameplayStatics::GetPlayerCharacter(this,0))P->SetActorLocation(PMLocation(0),false,nullptr,ETeleportType::TeleportPhysics);
 auto W=Cast<APMWorld>(UGameplayStatics::GetActorOfClass(this,APMWorld::StaticClass()));
 if(!W)W=GetWorld()->SpawnActor<APMWorld>();
 if(W) {
  W->SpawnVehicle(1,FVector(620,-750,150),FRotator(0,0,0));
  W->SpawnVehicle(2,FVector(1350,-750,150),FRotator(0,0,0));
  W->SpawnVehicle(8,FVector(1950,-750,150));
  W->SpawnVehicle(9,FVector(132500,-71200,-60));
  W->SpawnVehicle(10,FVector(-172000,-78200,160));
  W->SpawnVehicle(12,FVector(-178000,-87500,160));
 }
}

void APMWorld::Capture(float Dt) {
 CaptureTimer+=Dt;if(CaptureStage>0||CaptureTimer>7)FrameSamples.Add(Dt*1000);if(CaptureTimer<(CaptureStage==0?14.f:7.f))return;CaptureTimer=0;
 auto PC=Cast<APMController>(UGameplayStatics::GetPlayerController(this,0));if(!PC)return;
 Player->bInvulnerable=true;
 IFileManager::Get().MakeDirectory(*(FPaths::ProjectDir()/TEXT(".astra-run/screenshots")),true);
 auto Shot=[&](const TCHAR* Name) {
  FScreenshotRequest::RequestScreenshot(FPaths::ProjectDir()/TEXT(".astra-run/screenshots")/Name,true,false);
  FrameSamples.Sort();float Total=0;for(float T:FrameSamples)Total+=T;float Mean=FrameSamples.Num()?Total/FrameSamples.Num():0;float P95=FrameSamples.Num()?FrameSamples[FMath::Min(FrameSamples.Num()-1,int(FrameSamples.Num()*.95))]:0;
  UE_LOG(LogTemp,Display,TEXT("PM_CAPTURE %s: mean=%.2fms p95=%.2fms averageFPS=%.1f frames=%d people=%d vehicles=%d player=%s"),Name,Mean,P95,Mean>0?1000/Mean:0,FrameSamples.Num(),People.Num(),Vehicles.Num(),*Player->GetActorLocation().ToString());
 };
 switch(CaptureStage++) {
 case 0:Shot(TEXT("01_Downtown.png"));break;
 case 1:PC->ToggleMenu();break;
 case 2:Shot(TEXT("02_Services.png"));break;
 case 3:
  if(PC->bMenu)PC->ToggleMenu();Teleport(5);
  SpawnVehicle(12,PMLocation(5)+FVector(700,0,0));
  Player->SetActorLocation(PMLocation(5)+FVector(0,-600,0));PC->SetControlRotation(FRotator(-8,30,0));break;
 case 4:Shot(TEXT("03_Airfield.png"));break;
 case 5:Teleport(3);PC->SetControlRotation(FRotator(-8,15,0));break;
 case 6:Shot(TEXT("04_Eastport.png"));break;
 case 7:Teleport(0);Hour=23;Weather=0;WeatherUpdate();PC->SetControlRotation(FRotator(-8,15,0));break;
 case 8:Shot(TEXT("05_Night.png"));break;
 case 9:Hour=16;Weather=2;WeatherUpdate();break;
 case 10:Shot(TEXT("06_Rain.png"));break;
 case 11:Weather=0;SetWanted(3);LastKnown=Player->GetActorLocation();break;
 case 12:Shot(TEXT("07_Pursuit.png"));break;
 case 13:PC->bMap=true;PC->bWaypoint=true;PC->Waypoint=FVector(4200,3100,100);break;
 case 14:Shot(TEXT("08_Map.png"));break;
 case 15:PC->bMap=false;SetWanted(0);PC->Command(405);Player->bSuppressor=true;Player->bExtended=true;Player->bGrip=true;PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::RightMouseButton,IE_Pressed,1.f));break;
 case 16:Shot(TEXT("09_Equipment.png"));break;
 case 17:PC->ConsoleCommand(TEXT("quit"));break;
 }
 FrameSamples.Reset();
}
