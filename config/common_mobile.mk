# Inherit common mobile tequila stuff
$(call inherit-product, vendor/tequila/config/common.mk)

# Launcher3
PRODUCT_PACKAGES += \
    Launcher3QuickStep

PRODUCT_DEXPREOPT_SPEED_APPS += \
    Launcher3QuickStep

# Media
PRODUCT_SYSTEM_DEFAULT_PROPERTIES += \
    media.recorder.show_manufacturer_and_model=true

# SystemUI plugins
PRODUCT_PACKAGES += \
    QuickAccessWallet

# tequilaPapers
PRODUCT_PACKAGES += \
    tequilaPapers
