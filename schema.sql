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

create table if not exists comments(
    coid int not null auto_increment,
    uid int not null,
    content varchar(300) not null,
    cid int not null,
    primary key(coid)
);

create table if not exists teacher(
    tid int not null auto_increment,
    tname varchar(30),
    primary key(tid)
);

create table if not exists teaching(
    cid int not null,
    tid int not null,
    primary key(cid, tid)
);

create table if not exists incrementTable(
    addHash binary(10) not null,
    addTime timestamp(2), 
    opcode int not null,
    content varchar(350)
);
