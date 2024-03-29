create user user_name
    identified by 'user_password';

grant delete, insert, select, update on wordchainbot.* to bot_use;

create table guilds
(
    guild_id bigint unsigned not null
        primary key
);

create table languages
(
    lang   varchar(10)  not null
        primary key,
    lang_L varchar(100) not null
);

create table lang_chars
(
    lang          varchar(10) not null,
    special_chars varchar(10) not null,
    constraint lang_chars_languages_lang_fk
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
    constraint guilds_prop_guilds_guild_id_fk
        foreign key (guilds_id) references guilds (guild_id)
            on update cascade on delete cascade
);

create table guild_words
(
    guild_id         bigint unsigned not null,
    guild_channel_id bigint unsigned null,
    word             varchar(1000)   null,
    constraint guild_words_guilds_prop_guilds_id_fk
        foreign key (guild_id) references guilds_prop (guilds_id)
            on update cascade on delete cascade
);

INSERT INTO wordchainbot.lang_chars VALUES ('hu_HU', 'cs'), VALUES ('hu_HU', 'dz'), VALUES ('hu_HU', 'dzs'), VALUES ('hu_HU', 'gy'), VALUES ('hu_HU', 'ly'), VALUES ('hu_HU', 'ny'), VALUES ('hu_HU', 'sz'), VALUES ('hu_HU', 'ty'), VALUES ('hu_HU', 'zs');
INSERT INTO wordchainbot.languages VALUES ('hu_HU', 'Magyar'), ('en_US', 'English (US)'), ('en_GB', 'English (GB)')