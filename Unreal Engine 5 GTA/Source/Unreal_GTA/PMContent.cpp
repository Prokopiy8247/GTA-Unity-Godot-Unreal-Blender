#include "PMGame.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Components/AudioComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/StaticMesh.h"
#include "Sound/SoundBase.h"

const TArray<FPMVehicleSpec>& PMVehicles() {
 static TArray<FPMVehicleSpec> V={
 {TEXT("Cove compact"),TEXT("Compact"),0,395,175,3800,1100,1100},
 {TEXT("Meridian sedan"),TEXT("Sedan"),0,472,188,4800,1150,1450},
 {TEXT("Vesper GT"),TEXT("Sport"),0,445,194,7300,1900,1350},
 {TEXT("Ironwood muscle"),TEXT("Muscle"),0,495,196,6200,1550,1650},
 {TEXT("Ridge SUV"),TEXT("SUV"),0,496,202,4500,1050,2050},
 {TEXT("Foundry pickup"),TEXT("Pickup"),0,538,201,4300,1050,2100},
 {TEXT("Transit van"),TEXT("Van"),0,512,195,3500,800,2200},
 {TEXT("Patrol interceptor"),TEXT("Police"),0,485,194,5800,1550,1650},
 {TEXT("Kestrel motorcycle"),TEXT("Motorcycle"),1,215,78,6300,1800,260},
 {TEXT("Tide speedboat"),TEXT("Boat"),2,640,230,4000,850,1600},
 {TEXT("Heron helicopter"),TEXT("Helicopter"),3,920,250,6200,1500,2300},
 {TEXT("Police air support"),TEXT("PoliceHelicopter"),3,920,250,6500,1500,2400},
 {TEXT("Peregrine airplane"),TEXT("Airplane"),4,810,1100,11500,1500,1300}};
 return V;
}
const TArray<FPMWeaponSpec>& PMWeapons() {
 static TArray<FPMWeaponSpec> V={
 {TEXT("Unarmed"),TEXT(""),28,.52,0,180,0,1,false},
 {TEXT("M9 Sidearm"),TEXT("Pistol"),25,.22,.012,16000,15,1,false},
 {TEXT("Hawk revolver"),TEXT("Revolver"),62,.50,.008,22000,6,1,false},
 {TEXT("Swift SMG"),TEXT("SMG"),19,.085,.024,16000,30,1,true},
 {TEXT("Breach shotgun"),TEXT("Shotgun"),17,.82,.055,8000,8,8,false},
 {TEXT("AR-42 rifle"),TEXT("Rifle"),33,.115,.012,36000,30,1,true},
 {TEXT("Scout carbine"),TEXT("Carbine"),29,.10,.010,32000,30,1,true},
 {TEXT("Horizon marksman"),TEXT("Marksman"),78,.48,.004,60000,10,1,false},
 {TEXT("Longview sniper"),TEXT("Sniper"),130,1.10,.0008,110000,5,1,false},
 {TEXT("Fragment grenade"),TEXT("Grenade"),165,1.0,0,0,1,1,false},
 {TEXT("Lance launcher"),TEXT("Launcher"),300,1.65,0,0,1,1,false},
 {TEXT("Utility knife"),TEXT("Knife"),58,.40,0,190,0,1,false},
 {TEXT("Steel bat"),TEXT("Bat"),44,.68,0,220,0,1,false}};
 return V;
}
UStaticMesh* PMMesh(const FString& Name) {
 if(Name.IsEmpty()) return nullptr;
 const FString P=TEXT("/Game/GTA/Generated/SM_")+Name+TEXT(".SM_")+Name;
 return LoadObject<UStaticMesh>(nullptr,*P);
}
USoundBase* PMSound(const FString& Name) {
 const FString P=TEXT("/Game/GTA/Audio/")+Name+TEXT(".")+Name;
 return LoadObject<USoundBase>(nullptr,*P);
}
void PMPlay(UWorld* World,const FString& Name,FVector Location,float Volume,float Pitch) {
 if(USoundBase* Sound=PMSound(Name)) UGameplayStatics::PlaySoundAtLocation(World,Sound,Location,Volume,Pitch);
}
FVector PMLocation(int32 Index) {
 static const TArray<FVector> P={{1250,-1600,160},{0,74600,160},{0,-75400,160},{131500,-69550,170},{125000,74000,170},{-174000,-87000,170},{0,174600,160},{-150000,124600,160},{-75000,24600,160}};
 return P[FMath::Clamp(Index,0,P.Num()-1)];
}
FString PMDistrict(FVector P) {
 if(P.X>125000&&P.X<146000&&FMath::Abs(P.Y+70000)<1000)return TEXT("Eastport Docks");
 if(P.X>130000) return TEXT("Meridian Bay");
 if(P.X>105000) return P.Y<0?TEXT("Eastport Docks"):TEXT("Solace Coast");
 if(P.X<-100000 && P.Y<-25000) return TEXT("Meridian Airfield");
 if(P.X<-100000 && P.Y>50000) return TEXT("Cedar Highlands");
 if(P.Y>130000) return TEXT("North County");
 if(P.Y>50000) return TEXT("Willow Gardens");
 if(P.Y<-50000) return TEXT("Foundry District");
 if(P.X<-50000&&P.Y>-25000&&P.Y<50000)return TEXT("West Boulevard");
 return TEXT("Meridian Downtown");
}
APMSector::APMSector() {
 PrimaryActorTick.bCanEverTick=false;
 RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("SectorRoot"));
 RootComponent->SetMobility(EComponentMobility::Static);
}
void APMSector::Add(const FString& Name,FVector P,FRotator R,FVector S,int32 Cull) {
 UHierarchicalInstancedStaticMeshComponent* Batch=nullptr;
 const FName Key(*Name);
 for(auto C:Batches) if(C && C->ComponentTags.Contains(Key)) { Batch=C; break; }
 if(!Batch) {
  UStaticMesh* Mesh=PMMesh(Name); if(!Mesh) return;
  Batch=NewObject<UHierarchicalInstancedStaticMeshComponent>(this,NAME_None,RF_Transactional);
  Batch->ComponentTags.Add(Key); Batch->SetStaticMesh(Mesh);
  Batch->SetMobility(EComponentMobility::Static); Batch->SetupAttachment(RootComponent);
  Batch->SetCollisionProfileName(TEXT("BlockAll"));
  if(Name.StartsWith(TEXT("Tree"))||Name==TEXT("Marking")||Name==TEXT("Water")) Batch->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  Batch->SetCullDistances(Cull*.7f,Cull);
  if(Cull==0) Batch->SetCullDistances(0,0);
  AddInstanceComponent(Batch); Batch->RegisterComponent(); Batches.Add(Batch);
 }
 Batch->AddInstance(FTransform(R,P,S),false);
}
void APMSector::Generate() {
 for(auto C:Batches) if(C) C->DestroyComponent(); Batches.Empty();
 FRandomStream R(GridX*731+GridY*913+14701);
 const float X=GridX*25000, Y=GridY*25000;
 const bool Coast=X>=125000, Airport=X<=-125000&&Y<=-25000;
 const bool Rural=Y>=125000 || (X<=-100000&&Y>=50000);
 const bool Industry=Y<=-50000&&!Airport, Suburb=Y>=50000&&!Rural;
 if(Coast) {
  Add(TEXT("Water"),FVector(12500,12500,-125),FRotator::ZeroRotator,FVector(250,250,1),0);
  if(GridX==5) {
   Add(TEXT("Sand"),FVector(2000,12500,-30),FRotator::ZeroRotator,FVector(40,250,5),0);
   Add(TEXT("Sidewalk"),FVector(1200,12500,5),FRotator::ZeroRotator,FVector(8,250,2),0);
   for(int32 i=0;i<6;i++) Add(TEXT("Lamp"),FVector(800,i*4300,5));
  }
  if(GridY==3&&GridX==5) Add(TEXT("Lighthouse"),FVector(2000,5000,0),FRotator::ZeroRotator,FVector::OneVector,180000);
  if(GridY==-3&&GridX==5) {
   Add(TEXT("Sidewalk"),FVector(11000,5000,50),FRotator::ZeroRotator,FVector(200,16,20),0);
   for(int i=0;i<6;i++)Add(TEXT("Container"),FVector(4000+i*1600,4700,50));
   Add(TEXT("PortCrane"),FVector(8000,5000,50),FRotator(0,0,0),FVector::OneVector,160000);
  }
  return;
 }
 Add(TEXT("Ground"),FVector(12500,12500,-18),FRotator::ZeroRotator,FVector(250,250,8),0);
 Add(TEXT("Asphalt"),FVector(12500,0,0),FRotator::ZeroRotator,FVector(250,18,1),0);
 Add(TEXT("Asphalt"),FVector(0,12500,.15),FRotator::ZeroRotator,FVector(18,250,1),0);
 for(int i=0;i<25;i++) {
  Add(TEXT("Marking"),FVector(i*1000+500,-18,1.5),FRotator::ZeroRotator,FVector(4,.10,.08),40000);
  Add(TEXT("Marking"),FVector(i*1000+500,18,1.5),FRotator::ZeroRotator,FVector(4,.10,.08),40000);
  Add(TEXT("Marking"),FVector(0,i*1000+500,1.5),FRotator(0,90,0),FVector(4,.13,.08),40000);
 }
 if(Airport) {
  if(GridY==-4 || GridY==-3) {
   Add(TEXT("Asphalt"),FVector(12500,12500,2),FRotator::ZeroRotator,FVector(250,110,1),0);
   for(int i=0;i<12;i++)Add(TEXT("Marking"),FVector(i*2000,12500,4),FRotator::ZeroRotator,FVector(12,.6,.08));
  }
  if(GridY==-2) for(int i=0;i<3;i++) Add(TEXT("Hangar"),FVector(4300+i*7500,5500,0),FRotator(0,180,0),FVector::OneVector,110000);
  return;
 }
 if(Rural) {
  if(X<=-100000&&Y>=50000) Add(TEXT("Hill"),FVector(12500,12500,0),FRotator::ZeroRotator,FVector(1,1,1.25),220000);
  for(int i=0;i<45;i++) {
   const FVector P(R.FRandRange(1600,24000),R.FRandRange(1600,24000),0);
   Add(FString::Printf(TEXT("Tree%d"),R.RandRange(0,2)),P,FRotator(0,R.FRand()*360,0),FVector(R.FRandRange(.8,1.4)),80000);
   if(i%10==0)Add(TEXT("Rock"),P+FVector(350,0,0),FRotator::ZeroRotator,FVector(2.8),70000);
  }
  if(GridX%3==0&&GridY%2==0)Add(TEXT("House"),FVector(4000,5000,0),FRotator::ZeroRotator,FVector(1.2),100000);
  return;
 }
 Add(TEXT("Sidewalk"),FVector(12500,1190,12),FRotator::ZeroRotator,FVector(250,5.8,2),0);
 Add(TEXT("Sidewalk"),FVector(1190,12500,12),FRotator::ZeroRotator,FVector(5.8,250,2),0);
 Add(TEXT("Sidewalk"),FVector(12500,23810,12),FRotator::ZeroRotator,FVector(250,5.8,2),0);
 Add(TEXT("Sidewalk"),FVector(23810,12500,12),FRotator::ZeroRotator,FVector(5.8,250,2),0);
 for(int i=0;i<5;i++) {
  Add(TEXT("Lamp"),FVector(1800+i*5000,1090,12));
  Add(TEXT("Lamp"),FVector(1090,1800+i*5000,12),FRotator(0,-90,0));
  Add(TEXT("Tree0"),FVector(2200+i*5000,1700,10),FRotator::ZeroRotator,FVector(.8),45000);
  Add(TEXT("Bench"),FVector(3800+i*5000,1240,12),FRotator(0,180,0));
  if(i%2==0) Add(TEXT("Hydrant"),FVector(4800+i*5000,1040,12));
 }
 Add(TEXT("TrafficLight"),FVector(1060,1060,12),FRotator(0,180,0));
 Add(TEXT("BusStop"),FVector(9000,1180,12));
 Add(TEXT("Bin"),FVector(9350,1230,12));
 for(int ix=0;ix<4;ix++)for(int iy=0;iy<4;iy++) {
  FVector P(4200+ix*5450,4200+iy*5450,0);
  FString Mesh=Industry?TEXT("Warehouse"):(Suburb?TEXT("House"):TEXT("Office"));
  if(!Industry&&!Suburb) Mesh=R.FRand()<.30?TEXT("Tower"):R.FRand()<.5?TEXT("Apartment"):TEXT("Office");
  if(ix==0&&iy==0)Mesh=TEXT("Shop");
  if(GridX==0&&GridY==0&&ix==1&&iy==0)Mesh=TEXT("Safehouse");
  if(GridX==0&&GridY==-1&&ix==0&&iy==3)Mesh=TEXT("Garage");
  float Scale=Industry?.9f:Suburb?1.1f:R.FRandRange(.85,1.12);
  Add(Mesh,P,FRotator(0,iy%2==0?0:180,0),FVector(Scale,Scale,Mesh==TEXT("Tower")?R.FRandRange(.7,1.25):Scale),180000);
  if(Industry) for(int j=0;j<3;j++)Add(TEXT("Container"),P+FVector(0,2000+j*270,0),FRotator::ZeroRotator,FVector::OneVector,70000);
 }
 for(int i=0;i<8;i++) {
  Add(TEXT("Marking"),FVector(650+i*85,0,2),FRotator::ZeroRotator,FVector(.42,14,.08),25000);
  Add(TEXT("Marking"),FVector(0,650+i*85,2),FRotator::ZeroRotator,FVector(14,.42,.08),25000);
 }
}
