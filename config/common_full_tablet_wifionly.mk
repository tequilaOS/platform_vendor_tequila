$(call inherit-product, $(SRC_TARGET_DIR)/product/window_extensions.mk)

# Inherit full common tequila stuff
$(call inherit-product, vendor/tequila/config/common_full.mk)

# Required packages
PRODUCT_PACKAGES += \
    LatinIME

# Include tequila LatinIME dictionaries
PRODUCT_PACKAGE_OVERLAYS += vendor/tequila/overlay/dictionaries
PRODUCT_ENFORCE_RRO_EXCLUDED_OVERLAYS += vendor/tequila/overlay/dictionaries

# Settings
PRODUCT_PRODUCT_PROPERTIES += \
    persist.settings.large_screen_opt.enabled=true

$(call inherit-product, vendor/tequila/config/wifionly.mk)
