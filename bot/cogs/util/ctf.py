import json
import time
from typing import Union, NamedTuple
import requests
from datetime import datetime

import discord

from bot import ApplicationContext, BaseCog, Bot, Translator, cog_i18n

_ = Translator(__name__)

_T = Union[str, datetime]
TASKS_NAME = ["A", "B", "C", "D", "E", "F"]
SCORE_DEFAULT = [1, 100, 150, 200, 300, 0]


class UserData(NamedTuple):
    id: str
    data: tuple[_T, _T, _T, _T, _T, _T]
    total: int
    score: int


@cog_i18n
class CFTCog(BaseCog, name="CTF"):
    def __init__(self, bot: "Bot") -> None:
        super().__init__(bot)

        self.catch_data: list[UserData] = []
        self.last_catch_data_time = datetime.min
        self.get_rank()

    def get_rank(self) -> list[UserData]:
        if (datetime.now() - self.last_catch_data_time).total_seconds() < 60:
            return self.catch_data

        content = requests.get("http://homosserver.jp.eu.org:8080/").text.strip()
        data: dict[str, tuple[int, int, int, int]] = json.loads(
            content[:-2] + "}" if content.endswith(",}") else content
        )
        result: list[UserData] = []

        def format_time(x: int):
            return datetime.fromtimestamp(x) if x else None

        for id, user_data in data.items():
            if (len_id := len(id)) > 22 or len_id < 15:
                # print(f"Invalid id: {id}")
                continue
            if not sum(user_data):
                # print(f"no data: {id}")
                continue

            a, b, c, d, e, f = user_data
            user_data = UserData(
                id,
                tmp_data := (
                    format_time(a),
                    format_time(b),
                    format_time(c),
                    format_time(d),
                    format_time(e),
                    format_time(f),
                ),
                len(list(filter(bool, tmp_data))),
                sum([SCORE_DEFAULT[i] for i, x in enumerate(tmp_data) if x]),
            )
            result.append(user_data)

        self.last_catch_data_time = datetime.now()
        self.catch_data = sorted(result, key=lambda x: x.score, reverse=True)
        return self.catch_data

    @discord.slash_command(
        guild_only=True,
        i18n_name=_("ctf_rank"),
        i18n_description=_("CTF 比賽排名"),
    )
    async def ctf_rank(self, ctx: ApplicationContext):
        embed = discord.Embed(
            title="CTF Rank",
            color=discord.Color.random(),
            url="https://homosserver.jp.eu.org/",
        )

        embed.description = "\n".join(
            f"{i+1}. <@{user.id}> 共完成了 {user.total} 項\n"
            + "  ".join(
                f"  {TASKS_NAME[i]}: "
                + (
                    f"於 <t:{int(time.mktime(d.timetuple()))}> 完成作答"
                    if d is not None
                    else "尚未作答"
                )
                for i, d in enumerate(user.data)
            )
            for i, user in enumerate(self.get_rank())
        )

        await ctx.respond(embed=embed)


def setup(bot: "Bot"):
    bot.add_cog(CFTCog(bot))
