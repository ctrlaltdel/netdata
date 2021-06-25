import requests
import logging
import psutil
from bases.FrameworkServices.SimpleService import SimpleService

priority = 150000

ORDER = [
    "synced",
    "space",
    "difficulty",
    "height",
    "signage_point_index",
    "mempool_size",
    "balance",
    "plots_count",
    "plots_size",
]

CHARTS = {
    "synced": {
        "options": [None, "Sync status", None, None, None, "line"],
        "lines": [["synced", "synced", "absolute", 1, 1]],
    },
    "space": {
        "options": [None, "Network Space", "PiB", None, None, "line"],
        "lines": [["space", "space", "absolute", 1, 1024 ** 5]],
    },
    "difficulty": {
        "options": [None, "Network Difficulty", None, None, None, "line"],
        "lines": [["difficulty", "difficulty", "absolute", 1, 1]],
    },
    "height": {
        "options": [None, "height", None, None, None, "line"],
        "lines": [["height", "height", "absolute", 1, 1]],
    },
    "signage_point_index": {
        "options": [None, "signage_point_index", None, None, None, "line"],
        "lines": [["signage_point_index", "signage_point_index", "absolute", 1, 1]],
    },
    "mempool_size": {
        "options": [None, "mempool_size", None, None, None, "line"],
        "lines": [["mempool_size", "mempool_size", "absolute", 1, 1]],
    },
    "sub_slot_iters": {
        "options": [None, "sub_slot_iters", None, None, None, "line"],
        "lines": [["sub_slot_iters", "sub_slot_iters", "absolute", 1, 1]],
    },
    "plots_count": {
        "options": [None, "Number of plots", None, None, None, "line"],
        "lines": [
            ["count", "found", "absolute", 1, 1],
            ["not_found", "not_found", "absolute", 1, 1],
            ["failed_to_open", "failed_to_open", "absolute", 1, 1],
        ],
    },
    "plots_size": {
        "options": [None, "Total plots size", "B", None, None, "stacked"],
        "lines": [
            ["avail", "available", "absolute", 1, 1],
            ["used", "used", "absolute", 1, 1],
        ],
    },
    "balance": {
        "options": [None, "Wallet Balance", "XCH", None, None, "line"],
        "lines": [["balance", "balance", "absolute", 1, 10 ** 12]],
    },
    "cold_balance": {
        "options": [None, "Wallet Balance", "XCH", None, None, "line"],
        "lines": [["balance", "balance", "absolute", 1, 10 ** 12]],
    },
}


class Service(SimpleService):
    def __init__(self, configuration=None, name=None):
        SimpleService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS

        self.node_url = self.configuration.get("node_url", "https://localhost:8555")
        self.harvester_url = self.configuration.get(
            "harvester_url", "https://localhost:8560"
        )
        self.wallet_url = self.configuration.get("wallet_url", "https://localhost:9256")

        self.session = requests.Session()
        self.session.verify = False
        self.session.cert = (
            self.configuration.get(
                "ssl_certificate",
                "/home/ubuntu/.chia/mainnet/config/ssl/daemon/private_daemon.crt",
            ),
            self.configuration.get(
                "ssl_key",
                "/home/ubuntu/.chia/mainnet/config/ssl/daemon/private_daemon.key",
            ),
        )

    @staticmethod
    def check():
        return True

    def get_data(self):
        data = dict()

        resp = self.session.post(
            self.node_url + "/get_blockchain_state", data='{"":""}'
        ).json()

        if resp.get("success"):

            state = resp["blockchain_state"]

            #         {'blockchain_state': {'difficulty': 69,
            #                       'mempool_size': 0,
            #                       'peak': {'challenge_block_info_hash': '0x01dca9cd400b8ceba12f10fd3e9194f15d219c022e9e995a1f159304653c655d',
            #                                'challenge_vdf_output': {'data': '0x0100cd0308773894def5df2b0a05fadc4353fdebd04354a5834470baf5fcb99c8e199a9bc69f40e8701c2c7641a055d1a208fb17cb7dd4f3a0ee616005b7e9914808e8ae05ca8ac6801d9a7e39278b0c6d8953fc73f519a7db839cd65e6bf6e11c010500'},
            #                                'deficit': 0,
            #                                'farmer_puzzle_hash': '0x17485c3a5ec8f434060af267a256935d512dd8e1907d4c9a963c91c37452a042',
            #                                'fees': '1000000000000',
            #                                'finished_challenge_slot_hashes': None,
            #                                'finished_infused_challenge_slot_hashes': None,
            #                                'finished_reward_slot_hashes': None,
            #                                'header_hash': '0x74078dba1a823c5085984ec13fa7ad1d17330312f71f04ea01043ad91f8175df',
            #                                'height': 15453,
            #                                'infused_challenge_vdf_output': {'data': '0x01008e6dc390cae8d32bc970e43982ab9a71962ffc0fe21845c7a8a07a8ac176ab13d7ad5fc7910783298feaa9c2d72f56167f75aad424e6a909aa3bcb9559e1e91097aeefe6cd7637a01fc6177e28072f17f6a4ce7225d2a5dfc7f2faaa7b61820f0401'},
            #                                'overflow': False,
            #                                'pool_puzzle_hash': '0x17485c3a5ec8f434060af267a256935d512dd8e1907d4c9a963c91c37452a042',
            #                                'prev_hash': '0x2a91a3d6a474c17955c7c9c5ff6352c09c04d45c72a82b02a1acf59a778d68f9',
            #                                'prev_transaction_block_hash': '0xe893cf45b70e0166b8271bd62b1888a9be23ea2a1804d58759534575c2c8bcd5',
            #                                'prev_transaction_block_height': 15450,
            #                                'required_iters': '296734',
            #                                'reward_claims_incorporated': [{'amount': '1750000000000',
            #                                                                'parent_coin_info': '0x0000000000000000000000000000000000000000000000000000000000003c5a',
            #                                                                'puzzle_hash': '0xb16b445635f7db65ee96e03ed480783e4bf03fb971c530b00be93c3dc8f3192e'},
            #                                                               {'amount': '1250000000000',
            #                                                                'parent_coin_info': '0x6f79eeff2eac911836ec6bec71cda8710ba8f6c345eef8626bb100b65c347dcb',
            #                                                                'puzzle_hash': '0xb16b445635f7db65ee96e03ed480783e4bf03fb971c530b00be93c3dc8f3192e'},
            #                                                               {'amount': '1750000000000',
            #                                                                'parent_coin_info': '0x0000000000000000000000000000000000000000000000000000000000003c59',
            #                                                                'puzzle_hash': '0xb16b445635f7db65ee96e03ed480783e4bf03fb971c530b00be93c3dc8f3192e'},
            #                                                               {'amount': '250000000000',
            #                                                                'parent_coin_info': '0x26e99b51a5160a81f4cf107301cffbbcfd65ab3767fac05f08bf3806b51a35a0',
            #                                                                'puzzle_hash': '0xb16b445635f7db65ee96e03ed480783e4bf03fb971c530b00be93c3dc8f3192e'},
            #                                                               {'amount': '1750000000000',
            #                                                                'parent_coin_info': '0x0000000000000000000000000000000000000000000000000000000000003c58',
            #                                                                'puzzle_hash': '0x787590c41d3a0054dbc14740ecf5a9c2e670c3793fa69196ad6f59c32a6b08eb'},
            #                                                               {'amount': '250000000000',
            #                                                                'parent_coin_info': '0x1135063816de34499c1d559bf221178fbadbd12e2a97f612b24501f3a9245b1d',
            #                                                                'puzzle_hash': '0x787590c41d3a0054dbc14740ecf5a9c2e670c3793fa69196ad6f59c32a6b08eb'}],
            #                                'reward_infusion_new_challenge': '0xdd2be75c579d1a7cda42992e61cc8baa6f7c5b68f8790507671950b10ad1c38c',
            #                                'signage_point_index': 51,
            #                                'sub_epoch_summary_included': None,
            #                                'sub_slot_iters': '113901568',
            #                                'timestamp': '1615134903',
            #                                'total_iters': '48222140190',
            #                                'weight': '638873'},
            #                       'space': 35374685122582992,
            #                       'sub_slot_iters': 113901568,
            #                       'sync': {'sync_mode': False,
            #                                'sync_progress_height': 0,
            #                                'sync_tip_height': 0,
            #                                'synced': True}},
            #  'success': True}

            data["synced"] = 1 if state["sync"]["synced"] else 0
            data["difficulty"] = state["difficulty"]
            data["space"] = state["space"]
            data["sub_slot_iters"] = state["sub_slot_iters"]
            data["height"] = state["peak"]["height"]
            data["signage_point_index"] = state["peak"]["signage_point_index"]
            data["mempool_size"] = state["mempool_size"]

        #
        # Wallet
        #

        cold_wallets = self.configuration.get("cold_wallets", [])

        for puzzle_hash in cold_wallets:
            resp = self.session.post(
                self.wallet_url + "/get_coin_records_by_puzzle_hash",
                json={"puzzle_hash": puzzle_hash},
            ).json()

            if resp.get("success"):
                coin_records = resp["coin_records"]

                amount = 0
                for record in coin_records:
                    if not record["spent"]:
                        amount += int(record["coin"]["amount"])

                dimension_id = "wallet-{}".format(puzzle_hash[2:10])
                if dimension_id not in self.charts["balance"]:
                    self.charts["balance"].add_dimension([dimension_id])

                data[dimension_id] = amount

        #
        # Harvester
        #

        plots = self.session.post(
            self.harvester_url + "/get_plots", data='{"":""}'
        ).json()

        if plots.get("success"):
            data["count"] = len(plots["plots"])
            data["failed_to_open"] = len(plots["failed_to_open_filenames"])
            data["not_found"] = len(plots["not_found_filenames"])

            data["used"] = sum(plot["file_size"] for plot in plots["plots"])

            plot_directories = self.session.post(
                self.harvester_url + "/get_plot_directories", data='{"":""}'
            ).json()

            assert plot_directories.get("success")

            data["avail"] = 0
            for directory in plot_directories["directories"]:
                try:
                    data["avail"] += psutil.disk_usage(directory).free
                except FileNotFoundError:
                    pass

        return data
