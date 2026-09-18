#include "PMEditorLibrary.h"
#include "Misc/PackageName.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/Skeleton.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "Engine/World.h"
#include "WorldPartition/WorldPartition.h"
#include "WorldPartition/WorldPartitionRuntimeSpatialHash.h"
#if WITH_EDITOR
#include "PhysicsAssetUtils.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "UObject/UnrealType.h"
#endif
int32 UPMEditorLibrary::RepairCharacters() {
 int32 Count=0;
#if WITH_EDITOR
 for(const TCHAR* Name:{TEXT("Citizen"),TEXT("CitizenF"),TEXT("Police"),TEXT("Tactical")}) {
  FString Base=FString(TEXT("/Game/GTA/Generated/SK_"))+Name;
  USkeletalMesh* Mesh=LoadObject<USkeletalMesh>(nullptr,*Base);if(!Mesh)continue;
  FString SkeletonPath=Base+TEXT("_Skeleton");
  USkeleton* Skeleton=LoadObject<USkeleton>(nullptr,*SkeletonPath);
  if(!Skeleton) {
   UPackage* Package=CreatePackage(*SkeletonPath);
   Skeleton=NewObject<USkeleton>(Package,*FPackageName::GetShortName(SkeletonPath),RF_Public|RF_Standalone|RF_Transactional);
   if(!Skeleton->MergeAllBonesToBoneTree(Mesh))continue;
   FAssetRegistryModule::AssetCreated(Skeleton);
  }
  Mesh->SetSkeleton(Skeleton);Skeleton->MarkPackageDirty();
  FString PhysicsPath=Base+TEXT("_Physics");
  UPhysicsAsset* Physics=LoadObject<UPhysicsAsset>(nullptr,*PhysicsPath);
  if(!Physics) {
   UPackage* Package=CreatePackage(*PhysicsPath);
   Physics=NewObject<UPhysicsAsset>(Package,*FPackageName::GetShortName(PhysicsPath),RF_Public|RF_Standalone|RF_Transactional);
   FPhysAssetCreateParams Params;Params.MinBoneSize=5;FText Error;
   if(!FPhysicsAssetUtils::CreateFromSkeletalMesh(Physics,Mesh,Params,Error,true))UE_LOG(LogTemp,Warning,TEXT("PM physics: %s"),*Error.ToString());
   FAssetRegistryModule::AssetCreated(Physics);
  }
  Mesh->SetPhysicsAsset(Physics);Physics->MarkPackageDirty();Mesh->MarkPackageDirty();Count++;
  UE_LOG(LogTemp,Display,TEXT("PM_REPAIR %s: bones=%d bodies=%d"),Name,Mesh->GetRefSkeleton().GetNum(),Physics->SkeletalBodySetups.Num());
 }
#endif
 return Count;
}
bool UPMEditorLibrary::ConfigureWorld(AActor* Context) {
#if WITH_EDITOR
 if(!Context)return false;
 auto WP=Context->GetWorld()->GetWorldPartition();if(!WP)return false;
 WP->SetEnableStreaming(true);
 // Use UE's standard spatial hash so cell dimensions/loading radius are reproducible.
 if(!Cast<UWorldPartitionRuntimeSpatialHash>(WP->RuntimeHash))
  WP->RuntimeHash=NewObject<UWorldPartitionRuntimeSpatialHash>(WP,UWorldPartitionRuntimeSpatialHash::StaticClass(),NAME_None,RF_Transactional);
 if(FArrayProperty* Prop=FindFProperty<FArrayProperty>(WP->RuntimeHash->GetClass(),TEXT("Grids"))) {
  FScriptArrayHelper Grids(Prop,Prop->ContainerPtrToValuePtr<void>(WP->RuntimeHash));
  if(Grids.Num()==0)Grids.AddValue();
  for(int I=0;I<Grids.Num();I++) {
   auto Grid=reinterpret_cast<FSpatialHashRuntimeGrid*>(Grids.GetRawPtr(I));
   Grid->GridName=TEXT("Meridian");Grid->CellSize=25000;Grid->LoadingRange=85000;
  }
 }
 WP->MarkPackageDirty();Context->GetWorld()->MarkPackageDirty();return true;
#else
 return false;
#endif
}
