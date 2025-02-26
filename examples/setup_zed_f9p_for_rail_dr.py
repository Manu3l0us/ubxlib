#!/usr/bin/python3
"""
NEO-M9 sample code to configure timepulse
- Unlocked: 1 kHz, 50% duty cycle
- Locked: 1 kHz, 25% duty cycle

Run as module from project root:
python3 -m examples.set_timepulse_m9
"""
import logging

# from ubxlib.server import GnssUBlox     # Working on top of gpsd
from ubxlib.server_tty import GnssUBlox     # TTY direct backend
from ubxlib.cfgkeys import UbxKeyId, CfgKeyValues
from ubxlib.ubx_cfg_valset import UbxCfgValSetAction
from ubxlib.ubx_cfg_valget import UbxCfgValGetPoll


FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('ubxlib')
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

# Create UBX library, assumes 115'200 bps when using TTY backend
ubx = GnssUBlox('/dev/ttyS3', baudrate=921600)
ubx.setup()

poll_signals = UbxCfgValGetPoll([
    UbxKeyId.CFG_SIGNAL_GPS_ENA,        # Result will be in data0
    UbxKeyId.CFG_SIGNAL_GPS_L1CA_ENA,
    UbxKeyId.CFG_SIGNAL_GAL_ENA,
    UbxKeyId.CFG_SIGNAL_GAL_E1_ENA,
    UbxKeyId.CFG_SIGNAL_BDS_ENA,
    UbxKeyId.CFG_SIGNAL_BDS_B1_ENA,
    UbxKeyId.CFG_SIGNAL_GLO_ENA,
    UbxKeyId.CFG_SIGNAL_GLO_L1_ENA,
    UbxKeyId.CFG_SIGNAL_SBAS_ENA,
    UbxKeyId.CFG_SIGNAL_SBAS_L1CA_ENA        # Result will be in data9
])

res = ubx.poll(poll_signals)
print(f'Current GNSS system configuration\n{res}')

# Define configuration,
#  Set key = value pairs
#  Convert them to a list of CfgKeyData items for UbxCfgValSetAction()
cfg_keyvals = CfgKeyValues.from_keyvalues([
    # Enable antenna supply and set correct polarity, disable for MEWA
    (UbxKeyId.CFG_HW_ANT_CFG_VOLTCTRL, True),   
    (UbxKeyId.CFG_HW_ANT_CFG_PWRDOWN_POL, False),

    (UbxKeyId.CFG_TP_LEN_TP1, 200000),          # Specify pulse interval in us

    # Select Dynamic Model (RAIL=13)
    (UbxKeyId.CFG_NAVSPG_DYNMODEL, 13),

    # Mounting angle has to be set manually
    (UbxKeyId.CFG_SFIMU_AUTO_MNTALG_ENA, False),

    # Angles in centidegrees, check documentation
    (UbxKeyId.CFG_SFIMU_IMU_MNTALG_YAW, 0),     # 0 - 36000 centidegrees
    (UbxKeyId.CFG_SFIMU_IMU_MNTALG_PITCH, 0),   # -9000 - 9000 centidegrees
    (UbxKeyId.CFG_SFIMU_IMU_MNTALG_ROLL, 0),    # -18000 - 18000 centidegrees

    # IMU to Antenna lever arm
    (UbxKeyId.CFG_SFIMU_IMU2ANT_LA_X, 0),       # 16 bit signed in centimeters
    (UbxKeyId.CFG_SFIMU_IMU2ANT_LA_Y, 0),       # 16 bit signed in centimeters
    (UbxKeyId.CFG_SFIMU_IMU2ANT_LA_Z, 0),       # 16 bit signed in centimeters

    # IMU to VRP lever arm
    (UbxKeyId.CFG_SFODO_IMU2VRP_LA_X, 0),       # 16 bit signed in centimeters
    (UbxKeyId.CFG_SFODO_IMU2VRP_LA_Y, 0),       # 16 bit signed in centimeters
    (UbxKeyId.CFG_SFODO_IMU2VRP_LA_Z, 0),       # 16 bit signed in centimeters
    
    (UbxKeyId.CFG_SFODO_USE_WT_PIN, 1),         # Use the WT input
    (UbxKeyId.CFG_SFODO_DIS_AUTODIRPINPOL, 1),  # No automatic detection of direction polarity
    (UbxKeyId.CFG_SFODO_DIR_PINPOL, 0),         # 0 = High means forward
])

# Create CFG-VALSET message with the configuration key/values
cfg_setval = UbxCfgValSetAction(cfg_keyvals)

# Post message and check ACK/NAK result
ack_nak = ubx.set(cfg_setval)
print(ack_nak)      # Just print result, no further check

ubx.cleanup()
