#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/SaveGame.h"
#include "Blueprint/UserWidget.h"
#include "PMGame.generated.h"

class USoundBase; class UInstancedStaticMeshComponent; class UBoxComponent; class UStaticMeshComponent; class UPoseableMeshComponent; class UAudioComponent;
class USpringArmComponent; class UCameraComponent; class UPointLightComponent; class USpotLightComponent;
class UInputMappingContext; class UInputAction; class UButton; class UTextBlock; class UVerticalBox;
class UCanvasPanel; class UBorder; class UHierarchicalInstancedStaticMeshComponent; class UMaterialInstanceDynamic;
struct FInputActionValue;
class APMWorld; class APMVehicle; class APMHuman; class APMPlayer; class UPMHUD;

struct FPMVehicleSpec {
    FString Name, Mesh; int32 Kind; float Length, Width, MaxSpeed, Acceleration, Mass;
};
struct FPMWeaponSpec {
    FString Name, Mesh; float Damage, Interval, Spread, Range; int32 Magazine, Pellets; bool bAutomatic;
};
UNREAL_GTA_API const TArray<FPMVehicleSpec>& PMVehicles();
UNREAL_GTA_API const TArray<FPMWeaponSpec>& PMWeapons();
UNREAL_GTA_API UStaticMesh* PMMesh(const FString& Name);
UNREAL_GTA_API USoundBase* PMSound(const FString& Name);
UNREAL_GTA_API FString PMDistrict(FVector Location);
UNREAL_GTA_API FVector PMLocation(int32 Index);
UNREAL_GTA_API void PMPlay(UWorld* World, const FString& Name, FVector Location, float Volume=1.f, float Pitch=1.f);

UCLASS()
class UNREAL_GTA_API UPMSave : public USaveGame {
 GENERATED_BODY()
public:
 UPROPERTY() FVector Position=FVector(0,-650,180);
 UPROPERTY() float Health=100;
 UPROPERTY() float Armor=50;
 UPROPERTY() int32 Cash=15000;
 UPROPERTY() int32 Weapon=1;
 UPROPERTY() TArray<int32> Ammo;
 UPROPERTY() TArray<int32> Magazine;
 UPROPERTY() TArray<int32> Owned;
 UPROPERTY() float Hour=16;
 UPROPERTY() int32 Weather=0;
 UPROPERTY() int32 Outfit=0;
 UPROPERTY() TArray<float> Skills;
 UPROPERTY() TArray<int32> Garage;
 UPROPERTY() float Volume=.65f;
 UPROPERTY() int32 Quality=2;
 UPROPERTY() bool Suppressor=false;
 UPROPERTY() bool Extended=false;
 UPROPERTY() bool Grip=false;
 UPROPERTY() bool Scuba=false;
};

UCLASS()
class UNREAL_GTA_API APMSector : public AActor {
 GENERATED_BODY()
public:
 APMSector();
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Meridian") int32 GridX=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Meridian") int32 GridY=0;
 UPROPERTY() TArray<TObjectPtr<UHierarchicalInstancedStaticMeshComponent>> Batches;
 UFUNCTION(BlueprintCallable,CallInEditor,Category="Meridian") void Generate();
 void Add(const FString& Mesh,FVector P,FRotator R=FRotator::ZeroRotator,FVector Scale=FVector::OneVector,int32 Cull=45000);
};

UCLASS()
class UNREAL_GTA_API APMHuman : public ACharacter {
 GENERATED_BODY()
public:
 APMHuman();
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaSeconds) override;
 virtual float TakeDamage(float Damage,const FDamageEvent& Event,AController* Instigator,AActor* Causer) override;
 UPROPERTY(VisibleAnywhere) TObjectPtr<UPoseableMeshComponent> Body;
 UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Gun;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Meridian") bool bPolice=false;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Meridian") int32 Variant=0;
 UPROPERTY() TObjectPtr<APMWorld> WorldManager;
 float Health=100, Panic=0, Think=0, ShotTimer=0, WalkPhase=0, DeadTime=0;
 bool bDead=false, bTactical=false, bWitness=false;
 FVector Target=FVector::ZeroVector;
 TArray<FTransform> RestPose;
 void Dress(int32 Style);
 void Animate(float Dt,float Speed,bool Aim=false,bool Seated=false);
 void Die(FVector Impulse);
 bool CanSee(AActor* Other,float Range=14000) const;
 void AI(float Dt);
};

UCLASS()
class UNREAL_GTA_API APMPlayer : public APMHuman {
 GENERATED_BODY()
public:
 APMPlayer();
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaSeconds) override;
 virtual void Landed(const FHitResult& Hit) override;
 virtual float TakeDamage(float Damage,const FDamageEvent& Event,AController* Instigator,AActor* Causer) override;
 UPROPERTY(VisibleAnywhere) TObjectPtr<USpringArmComponent> Boom;
 UPROPERTY(VisibleAnywhere) TObjectPtr<UCameraComponent> Camera;
 UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Chute;
 UPROPERTY() TObjectPtr<APMVehicle> Vehicle;
 UPROPERTY() TObjectPtr<USpotLightComponent> Torch;
 UPROPERTY() TObjectPtr<UStaticMeshComponent> SuppressorMesh;
 UPROPERTY() TObjectPtr<UStaticMeshComponent> GripMesh;
 UPROPERTY() TObjectPtr<UStaticMeshComponent> MagazineMesh;
 float Armor=50, Breath=100, Stamina=100, FireTimer=0, ReloadTimer=0, HurtTimer=0, RespawnTimer=0;
 int32 Cash=15000, Weapon=1, Outfit=0;
 bool bAim=false,bFirstPerson=false,bInvulnerable=false,bInCover=false,bParachute=false,bScuba=false,bSuppressor=false,bExtended=false,bGrip=false;
 bool bWeaponWheel=false,bSwimming=false;
 FVector CoverNormal=FVector::ZeroVector;
 TArray<int32> Ammo, Reserve;
 TArray<bool> Owned;
 TArray<float> Skills;
 void Equip(int32 Index);
 void Fire();
 void Reload();
 void Interact();
 void EnterExit();
 void Cover();
 void Vault();
 void ToggleParachute();
 void Respawn(bool Arrest=false);
 void Save();
 void Load();
};

UCLASS()
class UNREAL_GTA_API APMVehicle : public APawn {
 GENERATED_BODY()
public:
 APMVehicle();
 virtual void BeginPlay() override;
 virtual void Tick(float Dt) override;
 virtual float TakeDamage(float Damage,const FDamageEvent& Event,AController* Instigator,AActor* Causer) override;
 UPROPERTY(VisibleAnywhere) TObjectPtr<UBoxComponent> Hull;
 UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Shell;
 UPROPERTY(VisibleAnywhere) TArray<TObjectPtr<UStaticMeshComponent>> Wheels;
 UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Rotor;
 UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Spoiler;
 UPROPERTY(VisibleAnywhere) TObjectPtr<UPoseableMeshComponent> DriverModel;
 UPROPERTY(VisibleAnywhere) TObjectPtr<UAudioComponent> EngineSound;
 UPROPERTY(VisibleAnywhere) TObjectPtr<UAudioComponent> SirenSound;
 UPROPERTY(VisibleAnywhere) TObjectPtr<USpotLightComponent> Headlights;
 UPROPERTY(VisibleAnywhere) TObjectPtr<UPointLightComponent> BeaconRed;
 UPROPERTY(VisibleAnywhere) TObjectPtr<UPointLightComponent> BeaconBlue;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Meridian") int32 Model=1;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Meridian") bool bTraffic=false;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Meridian") bool bPolice=false;
 UPROPERTY() TObjectPtr<APMPlayer> Driver;
 UPROPERTY() TObjectPtr<APMWorld> WorldManager;
 UPROPERTY() TObjectPtr<UMaterialInstanceDynamic> Paint;
 float Health=1000, Throttle=0, Steering=0, Lift=0, Speed=0, AITimer=0, FireClock=0, DamageTimer=0, RotorPhase=0, EngineUpgrade=1, BrakeUpgrade=1;
 float PathProgress=0;
 bool bBrake=false,bLights=true,bSiren=false,bDestroyed=false,bOccupied=false,bAircraft=false;
 FVector AITarget=FVector::ZeroVector;
 int32 Route=0, Segment=0;
 void Configure(int32 Index);
 void Drive(float Dt);
 void DriveAI(float Dt);
 void Repair();
 void Customize(int32 Option);
 void Explode();
 UFUNCTION() void Impact(UPrimitiveComponent* Hit,AActor* Other,UPrimitiveComponent* OtherComp,FVector Impulse,const FHitResult& Result);
};

UCLASS()
class UNREAL_GTA_API APMEffect : public AActor {
 GENERATED_BODY()
public:
 APMEffect();
 virtual void Tick(float Dt) override;
 UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> Particles;
 UPROPERTY() TObjectPtr<UPointLightComponent> Light;
 float Life=0,Duration=1;
 int32 Kind=0;
 TArray<FVector> Velocities;
 void Init(int32 Type,FLinearColor Color,float Scale=1);
};

UCLASS()
class UNREAL_GTA_API APMProjectile : public AActor {
 GENERATED_BODY()
public:
 APMProjectile();
 virtual void Tick(float Dt) override;
 UPROPERTY() TObjectPtr<UStaticMeshComponent> Mesh;
 FVector Velocity;
 float Fuse=3,Damage=150;
 bool bRocket=false;
 UPROPERTY() TObjectPtr<AActor> Source;
 void Detonate();
};

UCLASS()
class UNREAL_GTA_API APMWorld : public AActor {
 GENERATED_BODY()
public:
 APMWorld();
 virtual void BeginPlay() override;
 virtual void Tick(float Dt) override;
 UPROPERTY() TObjectPtr<APMPlayer> Player;
 UPROPERTY() TArray<TObjectPtr<APMHuman>> People;
 UPROPERTY() TArray<TObjectPtr<APMVehicle>> Vehicles;
 UPROPERTY() TObjectPtr<AActor> Sun;
 UPROPERTY() TObjectPtr<AActor> Fog;
 UPROPERTY() TObjectPtr<AActor> Sky;
 UPROPERTY() TArray<TObjectPtr<UPointLightComponent>> StreetLights;
 int32 Wanted=0, Weather=0;
 float Heat=0, Unseen=0, WitnessTimer=0, PopulationTimer=0, WeatherTimer=0, Hour=16, PoliceTimer=0, Clock=0;
 bool bPursuit=false,bTraffic=true,bPedestrians=true,bFreezeTime=false;
 FVector LastKnown=FVector::ZeroVector;
 FString Notice=TEXT("Welcome to Port Meridian");
 float NoticeTime=8;
 UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> Rain;
 UPROPERTY() TObjectPtr<UAudioComponent> Ambience;
 UPROPERTY() TObjectPtr<UAudioComponent> RainAudio;
 UPROPERTY() TObjectPtr<APMVehicle> TestCar;
 UPROPERTY() TObjectPtr<APMHuman> TestTarget;
 FVector TestStart;
 TArray<float> FrameSamples;
 bool bCapture=false; int32 CaptureStage=0; float CaptureTimer=0;
 TArray<int32> Garage;
 int32 SelectedVehicle=1;
 bool bSmokeTest=false; int32 SmokeStage=0; float SmokeTimer=0;
 void Message(const FString& Text,float Seconds=4);
 void Crime(float Severity,FVector Location,float NoiseRadius=6500,bool Force=false);
 void UpdateWanted(float Dt);
 void Populate();
 APMVehicle* SpawnVehicle(int32 Model,FVector Location,FRotator Rotation=FRotator::ZeroRotator,bool Traffic=false,bool Police=false);
 APMHuman* SpawnHuman(FVector Location,bool Police=false);
 void SetWanted(int32 Stars);
 void Teleport(int32 District);
 void WeatherUpdate();
 void Effect(FVector P,int32 Type,FLinearColor Color,float Scale=1);
 void Explosion(FVector P,float Radius,float Damage,AActor* Source);
 bool Visible(FVector From,FVector To,AActor* Ignore=nullptr) const;
 void SmokeTest(float Dt);
 void Capture(float Dt);
};

UCLASS()
class UNREAL_GTA_API APMController : public APlayerController {
 GENERATED_BODY()
public:
 virtual void BeginPlay() override;
 virtual void SetupInputComponent() override;
 virtual void PlayerTick(float Dt) override;
 UPROPERTY() TObjectPtr<UPMHUD> HUDWidget;
 UPROPERTY() TObjectPtr<UInputMappingContext> Mapping;
 UPROPERTY() TArray<TObjectPtr<UInputAction>> Actions;
 bool bMenu=false,bMap=false,bPaused=false;
 bool bWaypoint=false; FVector Waypoint=FVector::ZeroVector;
 int32 MenuPage=0;
 float SoundVolume=.65f; int32 GraphicsQuality=2;
 void ApplyPreferences();
 void MoveForward(const FInputActionValue& Value,float Sign);
 void MoveRight(const FInputActionValue& Value,float Sign);
 void LookYaw(const FInputActionValue& Value);
 void LookPitch(const FInputActionValue& Value);
 void Key(const FInputActionValue& Value,int32 Id);
 void ToggleMenu();
 void Command(int32 Id);
 APMPlayer* Player() const;
 APMWorld* Manager() const;
};

UCLASS()
class UNREAL_GTA_API UPMMenuEntry : public UObject {
 GENERATED_BODY()
public:
 UPROPERTY() TObjectPtr<APMController> PC;
 int32 Id=0;
 UFUNCTION() void Click();
};

UCLASS()
class UNREAL_GTA_API UPMHUD : public UUserWidget {
 GENERATED_BODY()
public:
 virtual void NativeConstruct() override;
 virtual TSharedRef<SWidget> RebuildWidget() override;
 virtual int32 NativePaint(const FPaintArgs& Args,const FGeometry& Geometry,const FSlateRect& Culling,FSlateWindowElementList& Out,int32 Layer,const FWidgetStyle& Style,bool Enabled) const override;
 UPROPERTY() TObjectPtr<UCanvasPanel> RootCanvas;
 UPROPERTY() TObjectPtr<UBorder> MenuBorder;
 UPROPERTY() TObjectPtr<UVerticalBox> MenuList;
 UPROPERTY() TArray<TObjectPtr<UPMMenuEntry>> Entries;
 void RebuildMenu();
};

UCLASS()
class UNREAL_GTA_API APMGameMode : public AGameModeBase {
 GENERATED_BODY()
public:
 APMGameMode();
 virtual void StartPlay() override;
};
