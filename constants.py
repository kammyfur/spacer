def value_to_constant(value, filter_str=None):
    values = list(map(lambda x: x if x == value else None, Constants.values()))
    keys = []

    for i in range(len(values)):
        if values[i] is not None:
            keys.append(list(Constants.keys())[i])

    if filter_str is not None:
        keys = list(filter(lambda x: x.startswith(filter_str), keys))

    return keys[0]

Version = "0.3.1"

Versions = [
    "1.0",
    "1.1",
    "1.2"
]

Channels = [
    "FL",
    "FR",
    "FC",
    "LFE",
    "BL",
    "BR",
    "FLC",
    "FRC",
    "BC",
    "SL",
    "SR",
    "TC",
    "TFL",
    "TFC",
    "TFR",
    "TBL",
    "TBC",
    "TBR",
    "D",
    "DR",
    "WL",
    "WR",
    "SDL",
    "SDR",
    "LFE2",
    "TSL",
    "TSR",
    "BFC",
    "BFL",
    "BFR"
]

Constants = {
    # Channel configurations
    'CHANNELS_2_1': 3,
    'CHANNELS_2_2': 4,
    'CHANNELS_3_0': 3,
    'CHANNELS_3_1': 4,
    'CHANNELS_3_2': 5,
    'CHANNELS_4_0': 4,
    'CHANNELS_4_1': 5,
    'CHANNELS_4_2': 6,
    'CHANNELS_5_0': 5,
    'CHANNELS_5_1': 6,
    'CHANNELS_5_2': 7,
    'CHANNELS_6_0': 6,
    'CHANNELS_6_1': 7,
    'CHANNELS_6_2': 8,
    'CHANNELS_7_0': 7,
    'CHANNELS_7_1': 8,
    'CHANNELS_7_2': 9,
    'CHANNELS_8_0': 8,
    'CHANNELS_8_1': 9,
    'CHANNELS_8_2': 10,
    'CHANNELS_9_0': 9,
    'CHANNELS_9_1': 10,
    'CHANNELS_9_2': 11,
    'CHANNELS_10_0': 10,
    'CHANNELS_10_1': 11,
    'CHANNELS_10_2': 12,
    'CHANNELS_11_0': 11,
    'CHANNELS_11_1': 12,
    'CHANNELS_11_2': 13,
    'CHANNELS_22_0': 22,
    'CHANNELS_22_1': 23,
    'CHANNELS_22_2': 24,
    'CHANNELS_ATMOS_2_1_2': 5,
    'CHANNELS_ATMOS_3_1_2': 6,
    'CHANNELS_ATMOS_4_1_2': 7,
    'CHANNELS_ATMOS_4_1_4': 9,
    'CHANNELS_ATMOS_5_1_2': 8,
    'CHANNELS_ATMOS_5_1_4': 10,
    'CHANNELS_ATMOS_7_1_2': 10,
    'CHANNELS_ATMOS_7_1_4': 12,
    'CHANNELS_ATMOS_7_1_6': 14,
    'CHANNELS_ATMOS_9_1_2': 12,
    'CHANNELS_ATMOS_9_1_4': 14,
    'CHANNELS_ATMOS_9_1_6': 16,
    'CHANNELS_ATMOS_11_1_4': 16,
    'CHANNELS_ATMOS_11_1_8': 20,

    # Channel layouts
    'LAYOUT_3_0': 'FL; FR; BC',
    'LAYOUT_3_1': 'FL; FR; BC; LFE',
    'LAYOUT_4_0': 'FL; FR; FC; BC',
    'LAYOUT_4_1': 'FL; FR; FC; LFE; BC',
    'LAYOUT_5_0': 'FL; FR; FC; BL; BR',
    'LAYOUT_5_1': 'FL; FR; FC; LFE; BL; BR',
    'LAYOUT_6_0': 'FL; FR; FC; BC; SL; SR',
    'LAYOUT_6_1': 'FL; FR; FC; LFE; BC; SL; SR',
    'LAYOUT_7_0': 'FL; FR; FC; BL; BR; SL; SR',
    'LAYOUT_7_1': 'FL; FR; FC; LFE; BL; BR; SL; SR',
    'LAYOUT_8_0': 'FL; FR; FC; BL; BR; BC; SL; SR',
    'LAYOUT_8_1': 'FL; FR; FC; LFE; BL; BR; BC; SL; SR',
    'LAYOUT_9_0': 'FL; FR; FC; BL; BR; SL; SR; TFL; TFR',
    'LAYOUT_9_1': 'FL; FR; FC; LFE; BL; BR; SL; SR; TFL; TFR',
    'LAYOUT_11_0': 'FL; FR; FC; BL; BR; FLC; FRC; SL; SR; TFL; TFR',
    'LAYOUT_11_1': 'FL; FR; FC; LFE; BL; BR; FLC; FRC; SL; SR; TFL; TFR',
    'LAYOUT_22_2': 'FL; FR; FC; LFE; BL; BR; FLC; FRC; BC; SL; SR; TC; TFL; TFC; TFR; TBL; TBC; TBR; LFE2; TSL; TSR; BFC; BFL; BFR',
    'LAYOUT_ATMOS_5_1_2': 'FL; FR; FC; LFE; BL; BR; TFL; TFR',
    'LAYOUT_ATMOS_5_1_4': 'FL; FR; FC; LFE; BL; BR; TFL; TFR; TBL; TBR',
    'LAYOUT_ATMOS_7_1_2': 'FL; FR; FC; LFE; BL; BR; SL; SR; TFL; TFR',
    'LAYOUT_ATMOS_7_1_4': 'FL; FR; FC; LFE; BL; BR; SL; SR; TFL; TFR; TBL; TBR',
    'LAYOUT_ATMOS_11_1_4': 'FL; FR; FC; LFE; BL; BR; FLC; FRC; BC; SL; SR; TBL; TBR',

    # Stem configurations
    'STEMS_MANUAL': -2,  # Supported for Sep
    'STEMS_SIMPLE': -1,  # Supported for Sep
    'STEMS_ALL': 0,  # Supported for Sep
    'STEMS_VOCALS': 1,  # Supported for Sep
    'STEMS_BASS': 2,  # Supported for Sep
    'STEMS_PIANO': 3,  # Supported for Sep
    'STEMS_GUITAR': 4,  # Supported for Sep
    'STEMS_DRUMS': 5,  # Supported for Sep
    'STEMS_OTHER': 6,  # Supported for Sep
    'STEMS_LFE': 7,
    'STEMS_VOCALS_L': 8,
    'STEMS_VOCALS_R': 9,
    'STEMS_BASS_L': 10,
    'STEMS_BASS_R': 11,
    'STEMS_PIANO_L': 12,
    'STEMS_PIANO_R': 13,
    'STEMS_GUITAR_L': 14,
    'STEMS_GUITAR_R': 15,
    'STEMS_DRUMS_L': 16,
    'STEMS_DRUMS_R': 17,
    'STEMS_OTHER_L': 18,
    'STEMS_OTHER_R': 19,
    'STEMS_LFE_L': 20,
    'STEMS_LFE_R': 21,

    # Output formats
    'OUTPUT_WAV': 0,
    'OUTPUT_FLAC': 1,
    'OUTPUT_AC3': 2,
    'OUTPUT_EAC3': 3,
    'OUTPUT_AC4': 4,
    'OUTPUT_AAC': 5,

    # AI models
    'MODEL_LEGACY': "htdemucs_6s",
    'MODEL_STANDARD': "htdemucs",
    'MODEL_STANDARD_LG': "htdemucs_ft",
    'MODEL_STANDARD_XL': "htdemucs_mmi",
    'MODEL_DEFAULT': "mdx_extra",
    'MODEL_BETTER_MD': "mdx",
    'MODEL_BETTER_SM': "mdx_extra_q",
    'MODEL_BETTER_XS': "mdx_q",
}
