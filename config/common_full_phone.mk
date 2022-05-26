# Inherit full common tequila stuff
$(call inherit-product, vendor/tequila/config/common_full.mk)

# Required packages
PRODUCT_PACKAGES += \
    LatinIME

# Include tequila LatinIME dictionaries
PRODUCT_PACKAGE_OVERLAYS += vendor/tequila/overlay/dictionaries

# Enable support of one-handed mode
PRODUCT_PRODUCT_PROPERTIES += \
    ro.support_one_handed_mode=true

$(call inherit-product, vendor/tequila/config/telephony.mk)
