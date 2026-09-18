#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "PMEditorLibrary.generated.h"
UCLASS()
class UNREAL_GTA_API UPMEditorLibrary : public UBlueprintFunctionLibrary {
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable,Category="Meridian|Editor") static int32 RepairCharacters();
 UFUNCTION(BlueprintCallable,Category="Meridian|Editor") static bool ConfigureWorld(AActor* Context);
};
