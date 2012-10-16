"""Miscellaneous user-model utilities."""
from . import models


def user_networks():
    """
    Return list of sets of user IDs; each set is an isolated user network.

    """
    networks = []
    networks_by_user = {}

    for rel in models.Relationship.objects.all():
        fpid, tpid = rel.from_profile_id, rel.to_profile_id

        fpid_net = networks_by_user.get(fpid)
        tpid_net = networks_by_user.get(tpid)
        if fpid_net and tpid_net:
            fpid_net.update(tpid_net)
            networks_by_user[tpid] = fpid_net
            networks.remove(tpid_net)
        elif fpid_net:
            fpid_net.add(tpid)
            networks_by_user[tpid] = fpid_net
        elif tpid_net:
            tpid_net.add(fpid)
            networks_by_user[fpid] = tpid_net
        else:
            net = {fpid, tpid}
            networks.append(net)
            networks_by_user[tpid] = net
            networks_by_user[fpid] = net

    return networks
