from analysis.airtime_capacity import summary


def test_comparable_airtime_and_five_quantity_capacity():
    result = summary()
    assert round(result["raw_34b_ms"], 3) == 246.784
    assert round(result["residue_8b_ms"], 3) == 123.904
    assert round(result["packet_service_ratio"], 3) == 1.992
    assert result["crt_packets_per_complete_record"] == 15
    assert round(result["crt_complete_records_per_window"]) == 97
