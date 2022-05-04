

# Method copied from bluesky.tests.test_plans
def _retrieve_motor_positions(doc_collector, motors):
    """
    Retrieves the motor positions for the completed run.
    Parameters
    ----------
    `doc_collector`: DocCollector
        DocCollector object that contains data from a single run
    `motors`: list
        the list of motors for which positions should be collected.
    Returns
    -------
    the dictionary:
    {'motor_name_1': list of positions,
     'motor_name_2': list of positions, ...}
    """
    motor_names = [_.name for _ in motors]
    # Get the event list for the first run
    desc = next(iter(doc_collector.event.keys()))  # Descriptor
    event_list = doc_collector.event[desc]

    # Now collect the positions
    positions = {k: [] for k in motor_names}
    for event in event_list:
        for name in positions.keys():
            positions[name].append(event["data"][name])

    return positions
