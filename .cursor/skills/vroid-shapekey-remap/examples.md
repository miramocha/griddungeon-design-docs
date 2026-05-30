# VRoid shape key examples (`face.main`)

57 `Fcl_*` keys were renamed; 79 other keys left unchanged (ARKit, custom, Japanese).

## All / brow / eye

| Old | New |
|-----|-----|
| `Fcl_ALL_Neutral` | `vroidAllNeutral` |
| `Fcl_ALL_Angry` | `vroidAllAngry` |
| `Fcl_BRW_Joy` | `vroidBrowJoy` |
| `Fcl_EYE_Natural` | `vroidEyeNatural` |
| `Fcl_EYE_Close_L` | `vroidEyeCloseL` |
| `Fcl_EYE_Close_R` | `vroidEyeCloseR` |
| `Fcl_EYE_Iris_Hide` | `vroidEyeIrisHide` |

## Mouth

| Old | New |
|-----|-----|
| `Fcl_MTH_Close` | `vroidMouthClose` |
| `Fcl_MTH_A` | `vroidMouthA` |
| `Fcl_MTH_SkinFung` | `vroidMouthSkinFang` |
| `Fcl_MTH_SkinFung_R` | `vroidMouthSkinFangR` |

## Teeth (HA → Teeth, Fung → Fang)

| Old | New |
|-----|-----|
| `Fcl_HA_Hide` | `vroidTeethHide` |
| `Fcl_HA_Fung1` | `vroidTeethFang1` |
| `Fcl_HA_Fung1_Low` | `vroidTeethFang1Low` |
| `Fcl_HA_Short_Up` | `vroidTeethShortUp` |

## Left unchanged (examples)

| Name | Reason |
|------|--------|
| `Basis` | Rest basis |
| `browInnerUp` | ARKit / custom |
| `eyeBlinkLeft` | ARKit |
| `_mouthPress+CatMouth` | Custom combo |
| `あ`, `まばたき` | Japanese / legacy |

## MCP one-liner pattern

```python
import bpy
obj = bpy.data.objects["face.main"]
# ... import convert_fcl_shape_key ...
renamed = []
for kb in obj.data.shape_keys.key_blocks:
    new = convert_fcl_shape_key(kb.name)
    if new:
        old = kb.name
        kb.name = new
        renamed.append((old, new))
result = {"count": len(renamed)}
```
