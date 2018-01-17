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
#
# Structure is [<manufacturer>][<model>] then
#     roles = any N of (AV_source|AV_switch|speaker|display)
#     supports = any N pf (PowerController|ChannelController|InputController|PlaybackController|StepSpeaker|Speaker)


DEVICE_DB = {
                'Panasonic':
                    { 'DMP-BDT110EB':
                        {
                            'roles': { 'AV_source' },
                            'supports': { 'PowerController', 
                                          'PlaybackController' },
                            'IRcodes': {
                                'Eject': 'K 2627 1123 11DD 019D 0244 019D 0244 019E 0243 019E 0243 019E 0243 019E 062A 019D 0244 019D 0246 019D 0244 019D 0243 019D 0244 019D 0244 0183 025E 0182 025E 0182 0244 019D 0244 019D 11F7 0184 062A 019E 062A 019E 062A 019E 0243 019E 062A 019D 0246 019C 0246 019D 0243 019E 0243 019E 0244 019D 0243 019E 0244 019D 0244 019D 062A 0183 062A 019E 062A 019E 062A 019E 062A 019E 062A 019E 062A 019E 2000',
                                'PowerToggle': '#IR code name:K 2627 1172 118D 01D1 0211 01D0 0210 01D1 0210 01D0 0211 01D0 0210 01CF 05F7 01D0 0212 01E9 01F7 01D0 0211 01E8 01F8 01D0 0210 01D1 0210 01B6 0210 01D0 0210 01E9 01F8 01D0 0210 01CF 11C5 01B6 05F7 01EC 05DC 01D1 05F6 01D0 0212 01CF 0211 01CF 0211 01D0 0211 01D0 0211 01E8 01F7 01E9 01F8 01E9 01F7 01D0 0211 01D0 05F6 01D1 05DC 01D1 05F7 01D0 05F7 01D0 05F7 01D1 05F7 01D1 05F7 01CF 05F8 01D0 2000',
                                'Pause': 'K 2627 1158 118E 01D2 020F 01EA 01F7 01E7 01F8 01EA 01F7 01D1 0210 01EC 05DA 01D2 0210 01D1 0210 01D0 0210 01EA 01F6 01D0 0211 01D1 020F 01D2 020F 01EA 01F7 01E8 01F8 01B7 022A 01CB 11AE 01D3 05F5 01D2 05DB 01D1 05F6 01D2 0210 01E9 01F7 01D0 05F7 01D1 0210 01E9 01F8 01D0 05F6 01D2 05F6 01EC 01F6 01EA 01F7 01CF 05F7 01D2 01F6 01D2 05F5 01D1 05F6 01D1 0211 01D0 0210 01D0 05F7 01D1 05F7 01D0 2000',
                                'Play': 'K 2627 1157 118E 01D3 020F 01D1 0210 01EA 01F6 01E9 01F8 01D0 0210 01E9 05DD 01E2 01FE 01D3 020F 01E8 01F8 01D2 020E 01D2 020F 01D0 0211 01D1 020F 01EA 01F7 01D1 020F 01D1 0210 01D1 11AA 01D1 05F6 01D2 05F6 01D0 05DC 01D2 0210 01EA 01F6 01EA 01F6 01D2 05F6 01E9 01F8 01E8 05DD 01EA 01F7 01D1 0210 01E5 01FC 01D0 05F6 01EC 05DC 01D1 0210 01D1 05F6 01B8 020F 01D1 05F6 01D0 05F7 01D2 05F6 01D1 2000',
                                'Stop': 'K 2627 1157 11A9 01D2 0210 01B8 0228 01D3 020C 01B7 0210 01D2 020F 01E9 05DC 01EA 01F7 01E9 01F7 01D1 0210 01D1 0210 01D1 020F 01D0 0211 01D0 0210 01E9 01F8 01E9 01F7 01D1 0210 01D0 11AA 01D2 05F6 01D1 05F6 01D2 05F6 01D1 0210 01D1 05F6 01D1 05DC 01CF 0212 01CF 0211 01D1 05F6 01D2 0210 01CF 0211 01D1 020F 01D0 0211 01D0 0210 01E9 05DD 01E9 05DD 01E9 01F8 01E8 05DE 01B6 05F7 01E9 05DD 01D0 2000',
                            },
                        },
                    },

                'Pioneer':
                    { 'PDP-LX50D':
                        {
                            'roles': { 'display' },
                            'supports': { 'PowerController' },
                            'IRcodes': {             
                                'PowerOn': 'K 2621 01F0 0211 0204 0646 0203 0212 01E9 0646 0204 0212 0204 0644 021C 01FA 0204 0644 0204 0646 0204 0212 0204 062B 0205 0211 0203 0646 021E 01F8 0203 0646 0204 0212 0203 0212 021D 062C 0204 0211 0203 062C 0203 0647 0204 0212 0203 0211 0203 0212 0201 0648 0204 0211 0203 0646 0204 0212 021C 01F9 0202 062E 0203 0646 0204 0646 0203 2000',
                                'PowerOff': 'K 2621 01F0 0212 0204 0644 0207 020E 0220 062A 0207 020E 0205 0644 01ED 022A 0203 062C 021F 062B 0205 0211 0204 0644 0206 020F 0205 0644 021E 01F8 0206 062A 0204 0211 0205 0644 0206 0643 0206 020F 0205 0644 0205 062B 021E 01F8 0205 0210 0204 0211 021F 01F6 0205 0210 0205 0644 0206 020F 0207 020F 021C 062C 0220 062A 0204 062C 0206 2000',
                                'InputHDMI1': 'K 2621 01F1 0644 021E 062C 0206 0643 0204 062C 0206 0210 0205 0643 0205 0211 0203 0646 021B 01FA 0204 0212 0203 0211 0204 0211 021E 062B 0204 0211 0204 062C 0204 0211 0204 0211 021D 062C 0203 0212 0204 0646 0204 0644 0205 062C 0204 0646 0203 0212 0203 0646 0205 0211 0204 0644 0204 0211 0204 0211 0203 0212 0203 0211 021D 0613 0203 2000',
                                'InputHDMI2': 'K 2621 01F0 0646 021E 0612 0204 0646 0204 0644 0204 0212 0203 0646 0204 0211 0203 062D 0203 0212 0202 0213 0202 0213 0201 0213 0201 0648 0203 0212 0202 0647 0202 0213 0201 0648 0203 062E 0202 0213 0201 0648 0201 0648 0202 0648 0202 0647 01ED 022A 01EA 0212 0200 0215 0201 0648 0203 0212 0201 0215 0201 0213 0201 0215 0200 0648 0203 2000',
                                'InputHDMI3': 'K 2620 01EF 0647 0203 0647 0203 062D 0204 0211 0204 0646 0204 0211 0202 0647 0204 0211 0204 0211 0202 0213 0202 0212 0202 0647 0204 0212 0201 062E 0204 0211 0203 0212 0203 0212 0201 0647 0204 0646 0204 0646 0204 062D 0201 0648 0203 0213 0202 0646 0203 0647 0202 0213 0203 0212 0203 0212 0201 0213 0202 0213 0202 062D 0201 2000'
                            },
                        },  
                    },

                'Amazon':
                    { 'Firestick':
                        {
                            'roles': { 'AV_source' },
                            'supports': { },
                            'IRcodes': {             
                            },
                        },  
                    },

                'Arcam':
                    { 'AVR360':
                        {
                            'roles': { 'AV_switch, speaker' },
                            'supports': { 'PowerController', 
                                          'StepSpeaker' },
                            'IRcodes': {             
                                'PowerOn': 'K 260B 06BD 0394 0358 070D 06EA 037B 0372 037A 0373 0394 0371 06F3 0359 0394 0356 0395 06EA 06F3 0371 037B 0357 2000',
                                #'PowerOff': 'K 260B 06BC 070E 0357 0394 06EF 0393 0371 037B 0371 037A 0357 070D 0359 0393 0359 0393 0359 0393 06EF 0393 0370 2000',
                                # Off = PVR (Airplay)
                                'PowerOff': 'K 260B 035E 037A 0374 0378 0357 0395 06D2 03AF 0371 037A 0371 037B 0358 070C 06EB 037A 0358 0394 0371 070F 06D0 2000',
                                'InputAUX': 'K 260C 0343 03B1 0357 0395 0356 0396 06CF 0395 0370 037C 036F 037C 0358 0394 0370 037B 038C 06F5 06D0 0396 0356 0395 0355 2000',
                                'InputBR': 'K 260B 035E 037A 06ED 070C 06EA 037B 0371 037B 0372 0379 0373 0379 0357 0395 0359 03AF 0371 06F3 06D2 0393 0359 2000',
                                'InputSAT': 'K 260C 0343 0395 06E9 06F5 06D0 0395 0357 0395 0356 0396 0373 0394 0356 0396 0370 037B 0370 037C 0356 0395 0370 037C 0356 2000',
                                'InputAV': 'K 260B 0343 0395 06E8 06F5 06EE 0394 0370 037C 0370 037B 0357 0395 0357 0395 0357 0394 0372 037A 0371 070F 06E9 2000',
                                'InputCD': 'K 260D 035A 037C 0356 0396 036E 037D 06CE 0396 0356 0396 036F 0399 036F 037C 0354 0397 0355 0397 0355 070F 036F 037C 0357 0395 0354 2000',
                                'InputPVR': 'K 260B 035E 037A 0374 0378 0357 0395 06D2 03AF 0371 037A 0371 037B 0358 070C 06EB 037A 0358 0394 0371 070F 06D0 2000',
                                'InputVCR': 'K 260C 0346 0393 0357 03B0 0359 0393 06EB 037A 0371 037B 0359 0393 0358 0393 0359 0393 0359 0393 0375 070C 0359 0393 06EB 2000',
                                'VolumeUp': 'K 260B 0343 0395 0706 06F2 06D2 0394 036A 0382 0370 037B 0358 0394 0357 070C 06EE 0394 0357 0395 0357 0395 0370 2000',
                                'VolumeDown': 'K 260C 035E 0396 0356 0396 0355 0396 06CF 0396 0356 0396 0354 0397 0355 0397 0354 072C 06CD 0397 0356 0396 0355 070F 036F 2000',
                                'Mute': 'K 260B 0360 0394 06E9 06F5 06CF 0396 0355 0397 0353 0398 036E 037D 0355 03B3 0355 070F 036F 037D 06E7 06F6 0358 2000',
                            },
                        }
                    },

                'Humax':
                    { 'DTR-T2100':
                        {
                            'roles': { 'AV_source' },
                            'supports': { 'PowerController', 
                                          'ChannelController' },
                            'IRcodes': {             
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
                            },
                        }         
                    }
             }