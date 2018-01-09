# Copyright 2018 Calum Loudon
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not 
# use this file except in compliance with the License. A copy of the License
# is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR 
# CONDITIONS OF ANY KIND, express or implied. See the License for the specific
# language governing permissions and limitations under the License.

# This file defines a set of commands and associated Keene KIRA IR commands for
# a range of devices.
#
# Ideally these would be auto-derived from an open source DB such as
# https://github.com/probonopd/irdb but for now hard code those devices we
# care about, based on capturing IR via a Keene receiver.

KIRA_IR_codes = {
                    'Panasonic':
                        { 'DMP-BDT110EB':
                            {
                                'Eject': 'K 2627 1123 11DD 019D 0244 019D 0244 019E 0243 019E 0243 019E 0243 019E 062A 019D 0244 019D 0246 019D 0244 019D 0243 019D 0244 019D 0244 0183 025E 0182 025E 0182 0244 019D 0244 019D 11F7 0184 062A 019E 062A 019E 062A 019E 0243 019E 062A 019D 0246 019C 0246 019D 0243 019E 0243 019E 0244 019D 0243 019E 0244 019D 0244 019D 062A 0183 062A 019E 062A 019E 062A 019E 062A 019E 062A 019E 062A 019E 2000'
                            },
                        },

                    'Pioneer':
                        { 'PDP-LX50D':
                            {
                                'PowerOn': '',
                                'PowerOff': '',
                                'InputHDMI1': '',
                                'InputHDMI2': '',
                                'InputHDMI3': '',
                            },  
                        },

                    'Arcam':
                        { 'AVR360':
                            {
                                'PowerOn': '',
                                'PowerOff': '',
                                'InputSAT': '',
                                'InputAV': '',
                            }
                        },

                    'Humax':
                        { 'DTR-T2100':
                            {
                                '0': 'K 2602 22E4 08D5 021D 2000',
                                '1': 'K 2602 22DE 08DA 0221 2000',
                                '2': 'K 2602 22E3 08D6 0220 2000',
                                '3': 'K 2602 22DE 08DB 0201 2000',
                                '4': 'K 2602 22F9 08DA 0220 2000',
                                '5': 'K 2602 22E3 08D6 021E 2000',
                                '6': 'K 2602 22F8 08DB 0206 2000',
                                '7': 'K 2602 22DF 08BF 021F 2000',
                                '8': 'K 2602 22F9 08DA 021D 2000',
                                '9': 'K 2602 22E1 08D8 021D 2000',
                                'PowerToggle': 'K 2602 22DF 08D9 021E 2000',
                                'Up': 'K 2602 22E3 08D6 021F 2000',
                                'Down': 'K 2602 22F9 08DA 021D 2000',
                                'Left': 'K 2602 22DE 08DB 0220 2000',
                                'Right': 'K 2602 22DE 08DB 0220 2000',
                                'OK': 'K 2602 22DE 08DA 021D 2000',
                                'Guide': 'K 2602 22F8 08DB 0201 2000',
                                'Menu': 'K 2602 22DE 08DB 0220 2000',
                                'Info': 'K 2602 22FD 08D7 0202 2000',
                                'Exit': 'K 2602 22DE 08DB 021B 2000',
                                'Delete': 'K 2602 22F9 08DA 0205 2000',
                                'MyView': 'K 2602 22E4 08D5 0221 2000',
                                'ChannelDown': 'K 2622 22E0 11AC 021D 0249 021C 0249 021E 0246 0206 0244 021E 0247 021E 0247 0205 025E 0205 0246 021C 0248 021D 0248 0203 0248 021E 0246 021D 0697 021D 0248 021D 0248 0205 0244 021E 0696 021D 0696 021E 0696 021F 0695 021D 0249 021D 0247 0205 025F 0203 0247 021C 0249 021D 0247 0205 0246 021D 0248 021C 0697 021E 0696 021D 0697 021D 0696 021D 2000'
                            }         
                        }
                }