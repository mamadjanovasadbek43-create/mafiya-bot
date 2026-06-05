import random

ROLES = {
    'don': {'name': '👑 Don', 'side': 'mafia', 'description': 'Siz Mafiya Donisiz!', 'ability': '🔫 /otish @username', 'can_shoot': True},
    'mafia': {'name': '🌙 Mafia', 'side': 'mafia', 'description': 'Siz Mafiasiz!', 'ability': '🔫 /otish @username', 'can_shoot': True},
    'manyak': {'name': '💣 Manyak', 'side': 'mafia', 'description': 'Siz Manyaksiz!', 'ability': '💣 /portlatish @username', 'can_shoot': True},
    'fohisha': {'name': '💋 Fohisha', 'side': 'mafia', 'description': 'Siz Fohishasiz!', 'ability': '💋 /sevish @username', 'can_shoot': False},
    'tinch': {'name': '☀️ Tinch', 'side': 'peace', 'description': 'Siz Tinch fuqarosiz!', 'ability': '🗳 /ovoz @username', 'can_shoot': False},
    'detektiv': {'name': '🔍 Detektiv', 'side': 'peace', 'description': 'Siz Detektivsiz!', 'ability': '🔍 /tekshirish @username', 'can_shoot': False},
    'doktor': {'name': '💊 Doktor', 'side': 'peace', 'description': 'Siz Doktorsiz!', 'ability': '💊 /davolash @username', 'can_shoot': False},
    'snayper': {'name': '🎯 Snayper', 'side': 'peace', 'description': 'Siz Snayperсиз!', 'ability': '🎯 /himoya @username', 'can_shoot': True},
}

ROLE_DISTRIBUTION = {
    4: ['don', 'mafia', 'detektiv', 'tinch'],
    5: ['don', 'mafia', 'detektiv', 'doktor', 'tinch'],
    6: ['don', 'mafia', 'manyak', 'detektiv', 'doktor', 'tinch'],
    7: ['don', 'mafia', 'manyak', 'detektiv', 'doktor', 'snayper', 'tinch'],
    8: ['don', 'mafia', 'mafia', 'manyak', 'detektiv', 'doktor', 'snayper', 'tinch'],
    9: ['don', 'mafia', 'mafia', 'manyak', 'fohisha', 'detektiv', 'doktor', 'snayper', 'tinch'],
    10: ['don', 'mafia', 'mafia', 'manyak', 'fohisha', 'detektiv', 'doktor', 'snayper', 'tinch', 'tinch'],
}

class Game:
    def __init__(self, chat_id, creator_id):
        self.chat_id = chat_id
        self.creator_id = creator_id
        self.players = {}
        self.status = "waiting"
        self.night = 0
        self.night_actions = {}
        self.votes = {}

    def add_player(self, user_id, name, username):
        if user_id in self.players:
            return "already"
        self.players[user_id] = {'id': user_id, 'name': name, 'username': username or str(user_id), 'role': None, 'alive': True}
        return "added"

    def assign_roles(self):
        count = len(self.players)
        role_list = ROLE_DISTRIBUTION.get(count, ROLE_DISTRIBUTION[10]).copy()
        while len(role_list) < count:
            role_list.append('tinch')
        random.shuffle(role_list)
        for i, (user_id, player) in enumerate(self.players.items()):
            player['role'] = role_list[i] if i < len(role_list) else 'tinch'

    def get_role_info(self, role):
        return ROLES.get(role, ROLES['tinch'])

    def get_player_by_username(self, username):
        username = username.lower()
        for player in self.players.values():
            if player['username'] and player['username'].lower() == username:
                return player
            if player['name'].lower() == username:
                return player
        return None

    def get_alive_players(self):
        return {uid: p for uid, p in self.players.items() if p['alive']}

    def add_night_action(self, actor_id, action, target_id):
        self.night_actions[actor_id] = {'action': action, 'target': target_id}

    def add_vote(self, voter_id, target_id):
        self.votes[voter_id] = target_id

    def check_voting_complete(self):
        alive = self.get_alive_players()
        return len(self.votes) >= len(alive)

    def get_voting_result(self):
        vote_count = {}
        for target_id in self.votes.values():
            vote_count[target_id] = vote_count.get(target_id, 0) + 1
        if not vote_count:
            return None
        max_votes = max(vote_count.values())
        candidates = [pid for pid, v in vote_count.items() if v == max_votes]
        return candidates[0] if len(candidates) == 1 else None

    def process_night_actions(self):
        results = {'killed': [], 'saved': False}
        heal_targets = set()
        protect_targets = set()
        seduced_players = set()
        for actor_id, action_data in self.night_actions.items():
            if action_data['action'] == 'seduce':
                seduced_players.add(action_data['target'])
        for actor_id, action_data in self.night_actions.items():
            if action_data['action'] == 'heal' and actor_id not in seduced_players:
                heal_targets.add(action_data['target'])
        for actor_id, action_data in self.night_actions.items():
            if action_data['action'] == 'protect' and actor_id not in seduced_players:
                protect_targets.add(action_data['target'])
        kill_votes = {}
        for actor_id, action_data in self.night_actions.items():
            if action_data['action'] in ['shoot', 'bomb'] and actor_id not in seduced_players:
                target = action_data['target']
                kill_votes[target] = kill_votes.get(target, 0) + 1
        for target_id in kill_votes:
            if target_id in heal_targets or target_id in protect_targets:
                results['saved'] = True
                continue
            if target_id in self.players and self.players[target_id]['alive']:
                self.players[target_id]['alive'] = False
                results['killed'].append(target_id)
        return results

    def eliminate_player(self, player_id):
        if player_id in self.players:
            self.players[player_id]['alive'] = False

    def check_winner(self):
        alive = self.get_alive_players()
        mafia_count = sum(1 for p in alive.values() if ROLES[p['role']]['side'] == 'mafia')
        peace_count = sum(1 for p in alive.values() if ROLES[p['role']]['side'] == 'peace')
        if mafia_count == 0:
            return "peace"
        if mafia_count >= peace_count:
            return "mafia"
        return None
