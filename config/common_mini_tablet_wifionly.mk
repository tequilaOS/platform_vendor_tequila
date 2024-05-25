# Inherit mini common tequila stuff
$(call inherit-product, vendor/tequila/config/common_mini.mk)

# Required packages
PRODUCT_PACKAGES += \
    LatinIME

$(call inherit-product, vendor/tequila/config/wifionly.mk)
