# Inherit common tequila stuff
$(call inherit-product, vendor/tequila/config/common_mobile.mk)

PRODUCT_SIZE := full

# Recorder
PRODUCT_PACKAGES += \
    Recorder
