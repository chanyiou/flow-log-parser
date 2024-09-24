import unittest
from unittest.mock import patch, mock_open
from flow_log_parser import load_lookup_table, parse_flow_log, write_output


class TestFlowLogParser(unittest.TestCase):

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="dstport,protocol,tag\n25,tcp,sv_P1\n68,udp,sv_P2\n",
    )
    def test_load_lookup_table(self, mock_file):
        lookup = load_lookup_table("dummy_path.csv")
        expected_lookup = {(25, "tcp"): "sv_p1", (68, "udp"): "sv_p2"}
        self.assertEqual(lookup, expected_lookup)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="2 123456789010 eni-1234 172.31.16.139 172.31.16.21 20641 22 6 20 4249 1418530010 1418530070 ACCEPT OK\n",
    )
    def test_parse_flow_log(self, mock_file):
        lookup = {(22, "tcp"): "sv_p1"}
        tag_counts, port_protocol_counts = parse_flow_log("dummy_path.log", lookup)
        self.assertEqual(tag_counts["sv_p1"], 1)
        self.assertEqual(port_protocol_counts[(22, "tcp")], 1)

    @patch("builtins.open", new_callable=mock_open)
    def test_write_output(self, mock_file):
        # Simulate output counts
        tag_counts = {
            "sv_p1": 2,
            "sv_p2": 1,
            "untagged": 1,
        }

        port_protocol_counts = {
            (22, "tcp"): 1,
            (80, "tcp"): 1,
        }

        # Call the function that writes the output
        write_output(tag_counts, port_protocol_counts, "output.txt")

        # Check the file handle that was used
        handle = mock_file()
        # Debug: Print all write calls to see the actual outputs
        print("Write calls:", handle.write.call_args_list)
        # Assert that the expected calls were made
        handle.write.assert_any_call("Tag Counts:\n")
        handle.write.assert_any_call("Tag             Count\n")
        handle.write.assert_any_call("sv_p1               2\n")
        handle.write.assert_any_call("sv_p2               1\n")
        handle.write.assert_any_call("untagged            1\n")
        handle.write.assert_any_call("\nPort/Protocol Combination Counts:\n")
        handle.write.assert_any_call("Port   Protocol   Count\n")
        handle.write.assert_any_call("22      tcp        1\n")
        handle.write.assert_any_call("80      tcp        1\n")


if __name__ == "__main__":
    unittest.main()
