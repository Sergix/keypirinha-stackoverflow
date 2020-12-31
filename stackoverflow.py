#
# Keypirinha StackOverflow Search Plugin
# Copyright (C) 2019  Sergix
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import keypirinha as kp
import keypirinha_util as kpu
import keypirinha_net as kpnet
import gzip, json
import urllib.parse

class StackOverflow(kp.Plugin):
	
	ITEM_CAT = kp.ItemCategory.USER_BASE + 1
	KEYWORD = 'stack'
	
	def __init__(self):
		super().__init__()
		self.opener = None
			
	def on_start(self):
		self.opener = kpnet.build_urllib_opener()
		self.opener.addheaders = [('Accept-Encoding', 'gzip')]

	def on_catalog(self):
		self.set_catalog([
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label="StackOverflow Search",
                short_desc="Search from StackOverflow",
                target="stack",
                args_hint=kp.ItemArgsHint.REQUIRED,
                hit_hint=kp.ItemHitHint.KEEPALL
            )
        ])
		
	def on_suggest(self, user_input, items_chain):
		if not items_chain or items_chain[0].category() != kp.ItemCategory.KEYWORD or not user_input:
			return
		
		if self.should_terminate(0.5):
			return

		suggestions = self.get_query(user_input)
		self.set_suggestions(suggestions, kp.Match.FUZZY, kp.Sort.DEFAULT)

	def on_events(self, flags):
		if flags & kp.Events.NETOPTIONS:
			self.on_start()

	def on_execute(self, item, action):
		kpu.shell_execute(item.short_desc())
		
	def get_query(self, input):
		answers = []
		url_string = 'https://api.stackexchange.com/2.2/search?site=stackoverflow&order=desc&sort=activity&pagesize=10&intitle='
		input_parsed = urllib.parse.quote_plus(input)
		url_string += input_parsed
		
		try:
			with self.opener.open(url_string) as request:
				response = gzip.decompress(request.read())
		except Exception as exc:
			self.err("Could not send request: ", exc)
			return answers
			
		content = json.loads(response.decode('utf-8'))["items"]

		for item in content:
			new_item = self.create_item(
				category=self.ITEM_CAT,
				label=item["title"],
				short_desc=item["link"],
				target=item["title"],
				args_hint=kp.ItemArgsHint.FORBIDDEN,
				hit_hint=kp.ItemHitHint.IGNORE
			)
			answers.append(new_item)
		
		return answers