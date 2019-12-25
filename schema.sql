drop database rema_server;
create database if not exists rema_server;
    
use rema_server;

create table if not exists user(
    uid int not null auto_increment,
    type char(1) not null default 'U',
    username varchar(20) unique not null,
    password varchar(20) not null,
    primary key(uid)
);

insert into user (uid, type, username, password) values 
    (1, 'A', 'karl-han', 'admin'), 
    (2, 'A', 'rema', 'admin');

create table if not exists course(
    cid int not null auto_increment,
    cname varchar(30),
    tid int not null,
    tname varchar(30),
    intro varchar(300),
    likes int not null default 0,
    uid int not null,
    primary key(cid)
);

insert into course (cid, cname, tid, tname, intro, uid) values 
    (1, '计算机安全学', 1, "Bintou", '学习与密码学相关知识，了解密码学历史', 0),
    (2, '编译原理', 2, "浴帘王子", '学习如何将代码转换成机器可执行代码的整个过程', 0);

create table if not exists comments(
    coid int not null auto_increment,
    uid int not null,
    content varchar(300) not null,
    cid int not null,
    primary key(coid)
);

insert into comments (uid, content, cid) values
    (1, '这门课真的不错', 1),
    (2, '这门课真的不错', 2);

create table if not exists teacher(
    tid int not null auto_increment,
    tname varchar(30),
    primary key(tid)
);

insert into teacher (tid, tname) values
    (1, 'Bintou'),
    (2, '浴帘王子');

create table if not exists teaching(
    cid int not null,
    tid int not null,
    primary key(cid, tid)
);

insert into teaching (cid, tid) values
    (1, 1), (2, 2);

create table if not exists incrementTable(
    addHash binary(10) not null,
    addTime timestamp(2), 
    opcode int not null,
    content varchar(350)
);
