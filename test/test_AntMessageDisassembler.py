import unittest
from gat.ant_stream_device import AntMessageDisassembler, AntMessageMarshaller
from gat.ant_msg_catalog import AntMessageCatalog

class Test(unittest.TestCase):

    def setUp(self):
        self.catalog = AntMessageCatalog(
                [   ("ANT_UnassignChannel", 0x41, "B", ["channelNumber"]),
                    ("ANT_AssignChannel", 0x42, "BBB", ["channelNumber", "channelType", "networkNumber"]),],
                [   ("ANT_ResetSystem", 0x4A, "x", []),
                    ("ANT_OpenChannel", 0x4B, "B", None),
                    ("ANT_CloseChannel", 0x4C, "B", ["channelNumber"]),])
        self.disasm = AntMessageDisassembler(self.catalog, AntMessageMarshaller()).disasm

    def test_disasm(self):
        # good message with named args + valid checksum
        m = self.disasm("\xA4\x03\x42\x04\x03\x40\xA2")
        self.assertEquals(m.sync, 0xA4)
        self.assertEquals(m.msg_id, 0x42)
        self.assertEquals(m.args.channelType, 0x03)
        self.assertEquals(m.args[2], 0x40)
        # good message but no named args availible
        m = self.disasm("\xA5\x01\x4B\x04\xEB")
        self.assertEquals(m.sync, 0xA5)
        self.assertEquals(m.msg_id, 0x4B)
        self.assertEquals(m.args[0], 0x04)
        # unkown message format should fail
        try: self.disasm("\xAB\x01\xBB\x00\x11")
        except KeyError: pass
        else: self.fail()
        # bad crc should fail
        try: self.disasm("\xA5\x01\x4B\x04\xEC")
        except AssertionError: pass
        else: self.fail()

    def test_disasm_lieniant(self):
        # good message, bad checksum
        m = self.disasm("\xA5\x01\x4B\x04\xEC", lieniant=True)
        self.assertEquals(m.args[0], 0x04)
        # well formed, but unkown message
        m = self.disasm("\xA4\x01\x00\x00\xA5", lieniant=True)
        self.assertEquals(m.sync, 0xA4)
        self.assertEquals(m.msg_id, 0x00)
        self.assertEquals(m.args[0], "a4010000a5")
        # arg count mismatch
        m = self.disasm("\xA4\x03\x42\x04\x03\x40\x00\xA2", lieniant=True)
        self.assertEquals(m.sync, 0xA4)
        self.assertEquals(m.msg_id, 0x42)
        self.assertEquals(m.args[0], "a4034204034000a2")


# vim: et ts=4 sts=4 nowrap
