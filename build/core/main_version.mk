# Build fingerprint
ifneq ($(BUILD_FINGERPRINT),)
ADDITIONAL_SYSTEM_PROPERTIES += \
    ro.build.fingerprint=$(BUILD_FINGERPRINT)
endif

# tequilaOS System Version
ADDITIONAL_SYSTEM_PROPERTIES += \
    ro.tequila.version=$(TEQUILA_VERSION) \
    ro.tequila.display.version=$(TEQUILA_DISPLAY_VERSION) \
    ro.tequila.releasetype=$(TEQUILA_BUILDTYPE) \
    ro.tequila.build.version=$(TEQUILA_PLATFORM_VERSION) \
    ro.modversion=$(TEQUILA_VERSION) \
