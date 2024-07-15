"""
Module containing a class providing support for systemd networkd .network files
"""
import os
import os.path

from snr.core.core import context
from snr.core.util.payloads import systemd_unit
from snr.core.util.payloads.systemd_unit import SystemdSectionType


__all__ = (
    "SYSTEMD_NETWORK_PATH", "SystemdNetwork"
)


def SYSTEMD_NETWORK_PATH(ctx: context.Context) -> str:  # pylint: disable=invalid-name
    """Return the path to systemd's network directory
    
    Args:
        ctx: Context
    
    Returns:
        The path to systemd's network directory
    """
    return ctx.join("usr", "lib", "systemd", "system")


class SystemdNetwork(systemd_unit.SystemdConfigFileBase,
                     root="/nonexistent",
                     base_sections=("Match", "Link", "SR_IOV",
                                    "Network", "Address", "Neighbor",
                                    "IPv6AddressLabel", "RoutingPolicyRule",
                                    "NextHop", "Route", "DHCPv4",
                                    "DHCPv6", "DHCPPrefixDelegation",
                                    "IPv6AcceptRA", "DHCPServer",
                                    "DHCPServerStaticLease",
                                    "IPv6SendRA", "IPv6Prefix",
                                    "IPv6RoutePrefix", "Bridge",
                                    "BridgeFDB", "BridgeMDB",
                                    "LLDP", "CAN", "IPoIB",
                                    "QDisc", "NetworkEmulator",
                                    "TokenBucketFilter", "PIE",
                                    "FlowQueuePIE", "StochasticFairBlue",
                                    "StochasticFairnessQueueing",
                                    "BFIFO", "PFIFO", "PFIFOHeadDrop",
                                    "PFIFOFast", "CAKE", "ControlledDelay",
                                    "DeficitRoundRobinScheduler",
                                    "DeficitRoundRobinSchedulerClass",
                                    "EnhancedTransmissionSelection",
                                    "GenericRandomEarlyDetection",
                                    "FairQueueingControlledDelay",
                                    "FairQueueing", "TrivialLinkEqualizer",
                                    "HierarchyTokenBucket",
                                    "HierarchyTokenBucketClass",
                                    "HeavyHitterFilter", "QuickFairQueueing",
                                    "QuickFairQueueingClass", "BridgeVLAN")):
    """Provide support for systemd networkd .network files
    """
    Match_section: SystemdSectionType = {}
    Link_section: SystemdSectionType = {}
    SR_IOV_section: SystemdSectionType = {}
    Network_section: SystemdSectionType = {}
    Address_section: SystemdSectionType = {}
    Neighbor_section: SystemdSectionType = {}
    IPv6AddressLabel_section: SystemdSectionType = {}
    RoutingPolicyRule_section: SystemdSectionType = {}
    NextHop_section: SystemdSectionType = {}
    Route_section: SystemdSectionType = {}
    DHCPv4_section: SystemdSectionType = {}
    DHCPv6_section: SystemdSectionType = {}
    DHCPPrefixDelegation_section: SystemdSectionType = {}
    IPv6AcceptRA_section: SystemdSectionType = {}
    DHCPServer_section: SystemdSectionType = {}
    DHCPServerStaticLease_section: SystemdSectionType = {}
    IPv6SendRA_section: SystemdSectionType = {}
    IPv6Prefix_section: SystemdSectionType = {}
    IPv6RoutePrefix_section: SystemdSectionType = {}
    Bridge_section: SystemdSectionType = {}
    BridgeFDB_section: SystemdSectionType = {}
    BridgeMDB_section: SystemdSectionType = {}
    LLDP_section: SystemdSectionType = {}
    CAN_section: SystemdSectionType = {}
    IPoIB_section: SystemdSectionType = {}
    QDisc_section: SystemdSectionType = {}
    NetworkEmulator_section: SystemdSectionType = {}
    TokenBucketFilter_section: SystemdSectionType = {}
    PIE_section: SystemdSectionType = {}
    FlowQueuePIE_section: SystemdSectionType = {}
    StochasticFairBlue_section: SystemdSectionType = {}
    StochasticFairnessQueueing_section: SystemdSectionType = {}
    BFIFO_section: SystemdSectionType = {}
    PFIFO_section: SystemdSectionType = {}
    PFIFOHeadDrop_section: SystemdSectionType = {}
    PFIFOFast_section: SystemdSectionType = {}
    CAKE_section: SystemdSectionType = {}
    ControlledDelay_section: SystemdSectionType = {}
    DeficitRoundRobinScheduler_section: SystemdSectionType = {}
    DeficitRoundRobinSchedulerClass_section: SystemdSectionType = {}
    EnhancedTransmissionSelection_section: SystemdSectionType = {}
    GenericRandomEarlyDetection_section: SystemdSectionType = {}
    FairQueueingControlledDelay_section: SystemdSectionType = {}
    FairQueueing_section: SystemdSectionType = {}
    TrivialLinkEqualizer_section: SystemdSectionType = {}
    HierarchyTokenBucket_section: SystemdSectionType = {}
    HierarchyTokenBucketClass_section: SystemdSectionType = {}
    HeavyHitterFilter_section: SystemdSectionType = {}
    QuickFairQueueing_section: SystemdSectionType = {}
    QuickFairQueueingClass_section: SystemdSectionType = {}
    BridgeVLAN_section: SystemdSectionType = {}
    _ctx: context.Context
    path: str
    root: str
    basename: str

    def __init__(self, ctx: context.Context, name: str):
        for extra_section in self._extra_sections:
            setattr(self, f"{extra_section}_section", {})
        for base_section in self._base_sections:
            setattr(self, f"{base_section}_section", {})
        self.root = SYSTEMD_NETWORK_PATH(ctx)
        self.path = os.path.join(self.root, name + self.suffix)
        self.basename = os.path.basename(self.path)
        self._ctx = ctx

    def write(self, make_dropin_dir: bool = True) -> None:
        self._write()
        if make_dropin_dir:
            os.mkdir(os.path.join(self.root, self.basename) + ".d")
