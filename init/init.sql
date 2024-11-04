create user bot_user
    identified by 'wordchainbot_testaccount1!';

grant delete, insert, select, update on wordchainbot.* to bot_user;
USE wordchainbot;
create table guilds
(
    guild_id bigint unsigned primary key
);

create table languages
(
    lang   varchar(10)  primary key,
    lang_L varchar(100) not null
);

create table lang_chars
(
    lang          varchar(10) not null,
    special_chars varchar(10) not null,
    foreign key (lang) references languages (lang)
);

create table guilds_prop
(
    guilds_id        bigint unsigned             not null,
    guild_channel_id bigint unsigned             null,
    guild_lang       varchar(10)                 null,
    last_sender_id   bigint unsigned             null,
    last_word        varchar(1000)               null,
    streak_count     bigint unsigned default '0' not null,
    pass_reaction    varchar(1000)               null,
    wrong_reaction   varchar(1000)               null,
    foreign key (guilds_id) references guilds (guild_id)
        on update cascade on delete cascade
);

create table guild_words
(
    guild_id         bigint unsigned not null,
    guild_channel_id bigint unsigned null,
    word             varchar(1000)   null,
    foreign key (guild_id) references guilds (guild_id)
        on update cascade on delete cascade
);

INSERT INTO languages VALUES ('hu_HU', 'Magyar'), ('en_US', 'English (US)'), ('en_GB', 'English (GB)');
INSERT INTO lang_chars VALUES ('hu_HU', 'cs'), ('hu_HU', 'dz'), ('hu_HU', 'dzs'), ('hu_HU', 'gy'), ('hu_HU', 'ly'), ('hu_HU', 'ny'), ('hu_HU', 'sz'), ('hu_HU', 'ty'), ('hu_HU', 'zs');