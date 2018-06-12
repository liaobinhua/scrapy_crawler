
DROP TABLE `first_reptile`;
CREATE TABLE `first_reptile` (
    `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'id',
    `title` varchar(255) NOT NULL DEFAULT '' COMMENT '名字',
    `create_date` date NULL COMMENT '写作时间',
    `url` varchar(300) NOT NULL DEFAULT '' COMMENT '爬取数据url',
    `url_object_id` varchar(50) NOT NULL DEFAULT '' COMMENT 'URL md5 ID',
    `front_image_url` varchar(300) NULL DEFAULT NULL COMMENT 'image url',
    `front_image_path` varchar(200) NULL DEFAULT NULL COMMENT 'image local path',
    `comment_nums` int(11) NULL DEFAULT '0' COMMENT '评论数 ',
    `fav_nums` int(11) NULL DEFAULT '0' COMMENT '收藏数',
    `praise_nums` int(11) NULL DEFAULT '0' COMMENT '点赞数',
    `tags` varchar(200) NULL COMMENT '标签',
    `content` MEDIUMTEXT NULL COMMENT '内容',
    PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE `zhihu_question`;
CREATE TABLE `zhihu_question`(
    `id` int(20) unsigned NOT NULL COMMENT 'zhihu id',
    `topics` varchar(255) NULL DEFAULT '' COMMENT '标签',
    `url` varchar(300) NOT NULL DEFAULT '' COMMENT '爬取数据url',
    `title` varchar(255) NOT NULL DEFAULT '' COMMENT '名字',
    `content` MEDIUMTEXT NULL COMMENT '内容',
    `create_time` datetime  NULL COMMENT 'create time',
    `update_time` datetime  NULL COMMENT 'update time',
    `answer_num` int(11) NULL DEFAULT '0' COMMENT '回答数',
    `comments_num` int(11) NULL DEFAULT '0' COMMENT '评论数 ',
    `watch_user_num`  int(11) NULL DEFAULT '0' COMMENT '关注数',
    `click_num` int(11) NULL DEFAULT '0' COMMENT '',
    `crawl_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE `zhihu_answer`;
CREATE TABLE `zhihu_answer`(
    `id` int(20) unsigned NOT NULL COMMENT 'zhihu id',
    `url` varchar(300) NOT NULL DEFAULT '' COMMENT '爬取数据url',
    `question_id` int(20) NOT NULL COMMENT 'question id',
    `author_id` varchar(50) NOT NULL COMMENT 'author id',
    `content` MEDIUMTEXT NULL COMMENT '内容',
    `praise_num` int(11) NULL DEFAULT '0' COMMENT '票数',
    `comments_num` int(11) NULL DEFAULT '0' COMMENT '评论数 ',
    `click_num` int(11) NULL DEFAULT '0' COMMENT '',
    `create_time` datetime  NULL COMMENT 'create time',
    `update_time` datetime  NULL COMMENT 'update time',
    `crawl_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
