include vendor/tequila/config/BoardConfigKernel.mk

ifeq ($(BOARD_USES_QCOM_HARDWARE),true)
include vendor/tequila/config/BoardConfigQcom.mk
endif

include vendor/tequila/config/BoardConfigSoong.mk
