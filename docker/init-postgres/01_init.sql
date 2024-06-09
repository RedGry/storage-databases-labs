-- Создание таблиц
CREATE TABLE if not exists category
(
    category_id INT PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    percent     DECIMAL      NOT NULL DEFAULT 0 CHECK ( percent >= 0 ),
    min_payment DECIMAL      NOT NULL DEFAULT 0 CHECK ( min_payment >= 0 )
);

CREATE TABLE if not exists client
(
    client_id     VARCHAR PRIMARY KEY,
    bonus_balance DECIMAL NOT NULL DEFAULT 0 CHECK ( bonus_balance >= 0 ),
    category_id   INT REFERENCES category (category_id)
);

CREATE TABLE if not exists dish
(
    dish_id VARCHAR PRIMARY KEY,
    name    VARCHAR(255) NOT NULL,
    price   DECIMAL      NOT NULL DEFAULT 0 CHECK ( price >= 0 )
);

CREATE TABLE if not exists payment
(
    payment_id  SERIAL PRIMARY KEY,
    client_id   VARCHAR REFERENCES client (client_id),
    dish_id     VARCHAR REFERENCES dish (dish_id),
    dish_amount INT       NOT NULL DEFAULT 0 CHECK (dish_amount >= 0),
    order_id    VARCHAR   NOT NULL,
    order_time  TIMESTAMP NOT NULL DEFAULT now(),
    order_sum   DECIMAL   NOT NULL DEFAULT 0 CHECK (order_sum >= 0),
    tips        DECIMAL   NOT NULL DEFAULT 0 CHECK (tips >= 0)
);

CREATE TABLE if not exists logs
(
    id         SERIAL PRIMARY KEY,
    time       TIMESTAMP,
    table_name VARCHAR(255),
    values     json
);

-- Настройка триггера для логирования
CREATE OR REPLACE FUNCTION log_changes()
    RETURNS TRIGGER AS
$$
BEGIN
    INSERT INTO logs (time, table_name, values)
    VALUES (now(), TG_TABLE_NAME, row_to_json(NEW));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Создание триггеров для каждой таблицы
CREATE TRIGGER log_client_changes
    AFTER INSERT OR UPDATE OR DELETE
    ON client
    FOR EACH ROW
EXECUTE FUNCTION log_changes();

CREATE TRIGGER log_category_changes
    AFTER INSERT OR UPDATE OR DELETE
    ON category
    FOR EACH ROW
EXECUTE FUNCTION log_changes();

CREATE TRIGGER log_dish_changes
    AFTER INSERT OR UPDATE OR DELETE
    ON dish
    FOR EACH ROW
EXECUTE FUNCTION log_changes();

CREATE TRIGGER log_payment_changes
    AFTER INSERT OR UPDATE OR DELETE
    ON payment
    FOR EACH ROW
EXECUTE FUNCTION log_changes();


-- category
insert into category(category_id, name, percent, min_payment)
values (1, 'Категория 1', 5, 1000),
       (2, 'Категория 2', 10, 1500),
       (3, 'Категория 3', 15, 2000),
       (4, 'Категория 4', 20, 2500),
       (5, 'Категория 5', 25, 3000);

-- client
insert into client(client_id, category_id, bonus_balance)
values ('66620d098179f92e55960ef6', 2, 1728),
       ('66620d098179f92e55960ef7', 3, 743),
       ('66620d098179f92e55960ef8', 1, 308),
       ('66620d098179f92e55960ef9', 2, 823),
       ('66620d098179f92e55960efa', 5, 2012),
       ('66620d098179f92e55960efb', 1, 2166),
       ('66620d098179f92e55960efc', 2, 1211),
       ('66620d098179f92e55960efd', 3, 270),
       ('66620d098179f92e55960efe', 3, 648),
       ('66620d098179f92e55960eff', 1, 1608);

-- dish
insert into dish(dish_id, name, price)
values ('66620d098179f92e55960f00', 'Ebiten maki', 917),
       ('66620d098179f92e55960f01', 'Bruschette with Tomato', 2254),
       ('66620d098179f92e55960f02', 'Pork Sausage Roll', 732),
       ('66620d098179f92e55960f03', 'Fish and Chips', 2429),
       ('66620d098179f92e55960f04', 'Mushroom Risotto', 1334),
       ('66620d098179f92e55960f05', 'Pork Sausage Roll', 599),
       ('66620d098179f92e55960f06', 'Salmon Nigiri', 2803),
       ('66620d098179f92e55960f07', 'Fettuccine Alfredo', 1763),
       ('66620d098179f92e55960f08', 'Bruschette with Tomato', 1657),
       ('66620d098179f92e55960f09', 'Mushroom Risotto', 2182),
       ('66620d098179f92e55960f0a', 'Bruschette with Tomato', 785),
       ('66620d098179f92e55960f0b', 'Risotto with Seafood', 2314),
       ('66620d098179f92e55960f0c', 'Cheeseburger', 2779),
       ('66620d098179f92e55960f0d', 'Cheeseburger', 951),
       ('66620d098179f92e55960f0e', 'Poutine', 567),
       ('66620d098179f92e55960f0f', 'Salmon Nigiri', 493),
       ('66620d098179f92e55960f10', 'Pasta Carbonara', 706),
       ('66620d098179f92e55960f11', 'Bunny Chow', 1572),
       ('66620d098179f92e55960f12', 'Risotto with Seafood', 1512),
       ('66620d098179f92e55960f13', 'Cheeseburger', 1915),
       ('66620d098179f92e55960f14', 'Vegetable Soup', 1992),
       ('66620d098179f92e55960f15', 'Pasta with Tomato and Basil', 1287),
       ('66620d098179f92e55960f16', 'Pasta with Tomato and Basil', 608),
       ('66620d098179f92e55960f17', 'Teriyaki Chicken Donburi', 765),
       ('66620d098179f92e55960f18', 'Salmon Nigiri', 296),
       ('66620d098179f92e55960f19', 'Tiramisù', 1679),
       ('66620d098179f92e55960f1a', 'French Toast', 2826),
       ('66620d098179f92e55960f1b', 'Scotch Eggs', 1335),
       ('66620d098179f92e55960f1c', 'Vegetable Soup', 2281),
       ('66620d098179f92e55960f1d', 'Pierogi', 565),
       ('66620d098179f92e55960f1e', 'Ebiten maki', 1726),
       ('66620d098179f92e55960f1f', 'Pappardelle alla Bolognese', 974),
       ('66620d098179f92e55960f20', 'Lasagne', 425),
       ('66620d098179f92e55960f21', 'Som Tam', 412),
       ('66620d098179f92e55960f22', 'Cheeseburger', 1926),
       ('66620d098179f92e55960f23', 'Bruschette with Tomato', 1927),
       ('66620d098179f92e55960f24', 'Meatballs with Sauce', 974),
       ('66620d098179f92e55960f25', 'Barbecue Ribs', 1117),
       ('66620d098179f92e55960f26', 'Arepas', 1759),
       ('66620d098179f92e55960f27', 'Pasta with Tomato and Basil', 1676),
       ('66620d098179f92e55960f28', 'Scotch Eggs', 1111),
       ('66620d098179f92e55960f29', 'Pork Belly Buns', 264),
       ('66620d098179f92e55960f2a', 'Caprese Salad', 2747),
       ('66620d098179f92e55960f2b', 'Tiramisù', 1326),
       ('66620d098179f92e55960f2c', 'Linguine with Clams', 2690),
       ('66620d098179f92e55960f2d', 'Bunny Chow', 2403),
       ('66620d098179f92e55960f2e', 'Chicken Wings', 1311),
       ('66620d098179f92e55960f2f', 'Pizza', 1767),
       ('66620d098179f92e55960f30', 'Pork Belly Buns', 2830),
       ('66620d098179f92e55960f31', 'Bunny Chow', 264);

-- payments
insert into payment(client_id, dish_id, dish_amount, order_id, order_time, order_sum, tips)
values ('66620d098179f92e55960ef6', '66620d098179f92e55960f06', 2, '66620d098179f92e55960f37',
        '2024-03-12T22:24:57.390337', 3402, 90),
       ('66620d098179f92e55960ef6', '66620d098179f92e55960f05', 2, '66620d098179f92e55960f37',
        '2024-03-12T22:24:57.390337', 3402, 797),
       ('66620d098179f92e55960ef7', '66620d098179f92e55960f09', 3, '66620d098179f92e55960f38',
        '2024-04-17T22:24:57.391842', 4433, 436),
       ('66620d098179f92e55960ef7', '66620d098179f92e55960f00', 3, '66620d098179f92e55960f38',
        '2024-04-17T22:24:57.391842', 4433, 618),
       ('66620d098179f92e55960ef7', '66620d098179f92e55960f04', 3, '66620d098179f92e55960f38',
        '2024-04-17T22:24:57.391842', 4433, 883),
       ('66620d098179f92e55960ef8', '66620d098179f92e55960f07', 3, '66620d098179f92e55960f39',
        '2024-04-09T22:24:57.391908', 4337, 87),
       ('66620d098179f92e55960ef8', '66620d098179f92e55960f08', 3, '66620d098179f92e55960f39',
        '2024-04-09T22:24:57.391908', 4337, 991),
       ('66620d098179f92e55960ef8', '66620d098179f92e55960f00', 3, '66620d098179f92e55960f39',
        '2024-04-09T22:24:57.391908', 4337, 753),
       ('66620d098179f92e55960ef9', '66620d098179f92e55960f08', 2, '66620d098179f92e55960f3a',
        '2024-03-04T22:24:57.391942', 2991, 164),
       ('66620d098179f92e55960ef9', '66620d098179f92e55960f04', 2, '66620d098179f92e55960f3a',
        '2024-03-04T22:24:57.391942', 2991, 301),
       ('66620d098179f92e55960efa', '66620d098179f92e55960f05', 3, '66620d098179f92e55960f3b',
        '2024-04-07T22:24:57.391971', 1797, 737),
       ('66620d098179f92e55960efa', '66620d098179f92e55960f05', 3, '66620d098179f92e55960f3b',
        '2024-04-07T22:24:57.391971', 1797, 775),
       ('66620d098179f92e55960efa', '66620d098179f92e55960f05', 3, '66620d098179f92e55960f3b',
        '2024-04-07T22:24:57.391971', 1797, 390),
       ('66620d098179f92e55960efb', '66620d098179f92e55960f08', 4, '66620d098179f92e55960f3c',
        '2024-03-26T22:24:57.392014', 8275, 833),
       ('66620d098179f92e55960efb', '66620d098179f92e55960f09', 4, '66620d098179f92e55960f3c',
        '2024-03-26T22:24:57.392014', 8275, 94),
       ('66620d098179f92e55960efb', '66620d098179f92e55960f09', 4, '66620d098179f92e55960f3c',
        '2024-03-26T22:24:57.392014', 8275, 792),
       ('66620d098179f92e55960efb', '66620d098179f92e55960f01', 4, '66620d098179f92e55960f3c',
        '2024-03-26T22:24:57.392014', 8275, 230),
       ('66620d098179f92e55960efc', '66620d098179f92e55960f07', 2, '66620d098179f92e55960f3d',
        '2024-05-10T22:24:57.392061', 3526, 280),
       ('66620d098179f92e55960efc', '66620d098179f92e55960f07', 2, '66620d098179f92e55960f3d',
        '2024-05-10T22:24:57.392061', 3526, 197),
       ('66620d098179f92e55960efd', '66620d098179f92e55960f02', 3, '66620d098179f92e55960f3e',
        '2024-04-29T22:24:57.392093', 5240, 328),
       ('66620d098179f92e55960efd', '66620d098179f92e55960f01', 3, '66620d098179f92e55960f3e',
        '2024-04-29T22:24:57.392093', 5240, 557),
       ('66620d098179f92e55960efd', '66620d098179f92e55960f01', 3, '66620d098179f92e55960f3e',
        '2024-04-29T22:24:57.392093', 5240, 203),
       ('66620d098179f92e55960efe', '66620d098179f92e55960f01', 2, '66620d098179f92e55960f3f',
        '2024-03-29T22:24:57.392128', 2986, 470),
       ('66620d098179f92e55960efe', '66620d098179f92e55960f02', 2, '66620d098179f92e55960f3f',
        '2024-03-29T22:24:57.392128', 2986, 37),
       ('66620d098179f92e55960eff', '66620d098179f92e55960f02', 4, '66620d098179f92e55960f40',
        '2024-04-04T22:24:57.392211', 5242, 785),
       ('66620d098179f92e55960eff', '66620d098179f92e55960f01', 4, '66620d098179f92e55960f40',
        '2024-04-04T22:24:57.392211', 5242, 91),
       ('66620d098179f92e55960eff', '66620d098179f92e55960f05', 4, '66620d098179f92e55960f40',
        '2024-04-04T22:24:57.392211', 5242, 95),
       ('66620d098179f92e55960eff', '66620d098179f92e55960f08', 4, '66620d098179f92e55960f40',
        '2024-04-04T22:24:57.392211', 5242, 110),
       ('66620d098179f92e55960ef6', '66620d098179f92e55960f10', 4, '66620d098179f92e55960f41',
        '2024-05-13T22:24:57.392282', 3496, 151),
       ('66620d098179f92e55960ef6', '66620d098179f92e55960f0a', 4, '66620d098179f92e55960f41',
        '2024-05-13T22:24:57.392282', 3496, 737),
       ('66620d098179f92e55960ef6', '66620d098179f92e55960f0f', 4, '66620d098179f92e55960f41',
        '2024-05-13T22:24:57.392282', 3496, 307),
       ('66620d098179f92e55960ef6', '66620d098179f92e55960f12', 4, '66620d098179f92e55960f41',
        '2024-05-13T22:24:57.392282', 3496, 803),
       ('66620d098179f92e55960ef7', '66620d098179f92e55960f10', 4, '66620d098179f92e55960f42',
        '2024-03-17T22:24:57.392319', 6008, 442),
       ('66620d098179f92e55960ef7', '66620d098179f92e55960f0c', 4, '66620d098179f92e55960f42',
        '2024-03-17T22:24:57.392319', 6008, 930),
       ('66620d098179f92e55960ef7', '66620d098179f92e55960f0d', 4, '66620d098179f92e55960f42',
        '2024-03-17T22:24:57.392319', 6008, 23),
       ('66620d098179f92e55960ef7', '66620d098179f92e55960f11', 4, '66620d098179f92e55960f42',
        '2024-03-17T22:24:57.392319', 6008, 33),
       ('66620d098179f92e55960ef8', '66620d098179f92e55960f12', 2, '66620d098179f92e55960f43',
        '2024-05-24T22:24:57.392354', 3084, 620),
       ('66620d098179f92e55960ef8', '66620d098179f92e55960f11', 2, '66620d098179f92e55960f43',
        '2024-05-24T22:24:57.392354', 3084, 91),
       ('66620d098179f92e55960ef9', '66620d098179f92e55960f0a', 2, '66620d098179f92e55960f44',
        '2024-05-14T22:24:57.392386', 1570, 231),
       ('66620d098179f92e55960ef9', '66620d098179f92e55960f0a', 2, '66620d098179f92e55960f44',
        '2024-05-14T22:24:57.392386', 1570, 890),
       ('66620d098179f92e55960efa', '66620d098179f92e55960f0a', 2, '66620d098179f92e55960f45',
        '2024-02-28T22:24:57.392411', 1491, 693),
       ('66620d098179f92e55960efa', '66620d098179f92e55960f10', 2, '66620d098179f92e55960f45',
        '2024-02-28T22:24:57.392411', 1491, 860),
       ('66620d098179f92e55960efb', '66620d098179f92e55960f10', 2, '66620d098179f92e55960f46',
        '2024-03-09T22:24:57.392435', 2621, 824),
       ('66620d098179f92e55960efb', '66620d098179f92e55960f13', 2, '66620d098179f92e55960f46',
        '2024-03-09T22:24:57.392435', 2621, 433),
       ('66620d098179f92e55960efc', '66620d098179f92e55960f13', 2, '66620d098179f92e55960f47',
        '2024-04-07T22:24:57.392465', 3427, 913),
       ('66620d098179f92e55960efc', '66620d098179f92e55960f12', 2, '66620d098179f92e55960f47',
        '2024-04-07T22:24:57.392465', 3427, 263),
       ('66620d098179f92e55960efd', '66620d098179f92e55960f13', 2, '66620d098179f92e55960f48',
        '2024-03-24T22:24:57.392497', 3427, 38),
       ('66620d098179f92e55960efd', '66620d098179f92e55960f12', 2, '66620d098179f92e55960f48',
        '2024-03-24T22:24:57.392497', 3427, 83),
       ('66620d098179f92e55960efe', '66620d098179f92e55960f10', 2, '66620d098179f92e55960f49',
        '2024-03-05T22:24:57.392590', 2218, 601),
       ('66620d098179f92e55960efe', '66620d098179f92e55960f12', 2, '66620d098179f92e55960f49',
        '2024-03-05T22:24:57.392590', 2218, 465),
       ('66620d098179f92e55960eff', '66620d098179f92e55960f12', 5, '66620d098179f92e55960f4a',
        '2024-05-09T22:24:57.392659', 6430, 451),
       ('66620d098179f92e55960eff', '66620d098179f92e55960f12', 5, '66620d098179f92e55960f4a',
        '2024-05-09T22:24:57.392659', 6430, 23),
       ('66620d098179f92e55960eff', '66620d098179f92e55960f10', 5, '66620d098179f92e55960f4a',
        '2024-05-09T22:24:57.392659', 6430, 256),
       ('66620d098179f92e55960eff', '66620d098179f92e55960f13', 5, '66620d098179f92e55960f4a',
        '2024-05-09T22:24:57.392659', 6430, 102),
       ('66620d098179f92e55960eff', '66620d098179f92e55960f0a', 5, '66620d098179f92e55960f4a',
        '2024-05-09T22:24:57.392659', 6430, 623),
       ('66620d098179f92e55960ef6', '66620d098179f92e55960f17', 2, '66620d098179f92e55960f4b',
        '2024-03-04T22:24:57.392877', 2757, 355),
       ('66620d098179f92e55960ef6', '66620d098179f92e55960f14', 2, '66620d098179f92e55960f4b',
        '2024-03-04T22:24:57.392877', 2757, 291),
       ('66620d098179f92e55960ef7', '66620d098179f92e55960f15', 3, '66620d098179f92e55960f4c',
        '2024-03-18T22:24:57.392937', 5792, 523),
       ('66620d098179f92e55960ef7', '66620d098179f92e55960f19', 3, '66620d098179f92e55960f4c',
        '2024-03-18T22:24:57.392937', 5792, 823),
       ('66620d098179f92e55960ef7', '66620d098179f92e55960f1a', 3, '66620d098179f92e55960f4c',
        '2024-03-18T22:24:57.392937', 5792, 291),
       ('66620d098179f92e55960ef8', '66620d098179f92e55960f17', 2, '66620d098179f92e55960f4d',
        '2024-03-13T22:24:57.392967', 2100, 444),
       ('66620d098179f92e55960ef8', '66620d098179f92e55960f1b', 2, '66620d098179f92e55960f4d',
        '2024-03-13T22:24:57.392967', 2100, 749),
       ('66620d098179f92e55960ef9', '66620d098179f92e55960f18', 2, '66620d098179f92e55960f4e',
        '2024-03-15T22:24:57.392996', 1975, 789),
       ('66620d098179f92e55960ef9', '66620d098179f92e55960f19', 2, '66620d098179f92e55960f4e',
        '2024-03-15T22:24:57.392996', 1975, 755),
       ('66620d098179f92e55960efa', '66620d098179f92e55960f1a', 4, '66620d098179f92e55960f4f',
        '2024-06-02T22:24:57.393027', 6761, 719),
       ('66620d098179f92e55960efa', '66620d098179f92e55960f14', 4, '66620d098179f92e55960f4f',
        '2024-06-02T22:24:57.393027', 6761, 283),
       ('66620d098179f92e55960efa', '66620d098179f92e55960f1b', 4, '66620d098179f92e55960f4f',
        '2024-06-02T22:24:57.393027', 6761, 56),
       ('66620d098179f92e55960efa', '66620d098179f92e55960f16', 4, '66620d098179f92e55960f4f',
        '2024-06-02T22:24:57.393027', 6761, 4),
       ('66620d098179f92e55960efb', '66620d098179f92e55960f17', 3, '66620d098179f92e55960f50',
        '2024-05-02T22:24:57.393054', 3811, 60),
       ('66620d098179f92e55960efb', '66620d098179f92e55960f1c', 3, '66620d098179f92e55960f50',
        '2024-05-02T22:24:57.393054', 3811, 9),
       ('66620d098179f92e55960efb', '66620d098179f92e55960f17', 3, '66620d098179f92e55960f50',
        '2024-05-02T22:24:57.393054', 3811, 697),
       ('66620d098179f92e55960efc', '66620d098179f92e55960f14', 2, '66620d098179f92e55960f51',
        '2024-03-29T22:24:57.393081', 2288, 977),
       ('66620d098179f92e55960efc', '66620d098179f92e55960f18', 2, '66620d098179f92e55960f51',
        '2024-03-29T22:24:57.393081', 2288, 248),
       ('66620d098179f92e55960efd', '66620d098179f92e55960f17', 4, '66620d098179f92e55960f52',
        '2024-03-22T22:24:57.393107', 5879, 651),
       ('66620d098179f92e55960efd', '66620d098179f92e55960f14', 4, '66620d098179f92e55960f52',
        '2024-03-22T22:24:57.393107', 5879, 259),
       ('66620d098179f92e55960efd', '66620d098179f92e55960f18', 4, '66620d098179f92e55960f52',
        '2024-03-22T22:24:57.393107', 5879, 424),
       ('66620d098179f92e55960efd', '66620d098179f92e55960f1a', 4, '66620d098179f92e55960f52',
        '2024-03-22T22:24:57.393107', 5879, 574),
       ('66620d098179f92e55960efe', '66620d098179f92e55960f1a', 4, '66620d098179f92e55960f53',
        '2024-06-06T22:24:57.393143', 5377, 315),
       ('66620d098179f92e55960efe', '66620d098179f92e55960f1b', 4, '66620d098179f92e55960f53',
        '2024-06-06T22:24:57.393143', 5377, 680),
       ('66620d098179f92e55960efe', '66620d098179f92e55960f16', 4, '66620d098179f92e55960f53',
        '2024-06-06T22:24:57.393143', 5377, 206),
       ('66620d098179f92e55960efe', '66620d098179f92e55960f16', 4, '66620d098179f92e55960f53',
        '2024-06-06T22:24:57.393143', 5377, 456),
       ('66620d098179f92e55960eff', '66620d098179f92e55960f17', 3, '66620d098179f92e55960f54',
        '2024-05-05T22:24:57.393172', 4926, 893),
       ('66620d098179f92e55960eff', '66620d098179f92e55960f1b', 3, '66620d098179f92e55960f54',
        '2024-05-05T22:24:57.393172', 4926, 477),
       ('66620d098179f92e55960eff', '66620d098179f92e55960f1a', 3, '66620d098179f92e55960f54',
        '2024-05-05T22:24:57.393172', 4926, 242),
       ('66620d098179f92e55960ef6', '66620d098179f92e55960f1f', 3, '66620d098179f92e55960f55',
        '2024-05-22T22:24:57.393203', 3624, 289),
       ('66620d098179f92e55960ef6', '66620d098179f92e55960f1f', 3, '66620d098179f92e55960f55',
        '2024-05-22T22:24:57.393203', 3624, 861),
       ('66620d098179f92e55960ef6', '66620d098179f92e55960f27', 3, '66620d098179f92e55960f55',
        '2024-05-22T22:24:57.393203', 3624, 502),
       ('66620d098179f92e55960ef7', '66620d098179f92e55960f26', 4, '66620d098179f92e55960f56',
        '2024-03-05T22:24:57.393231', 5433, 463),
       ('66620d098179f92e55960ef7', '66620d098179f92e55960f1f', 4, '66620d098179f92e55960f56',
        '2024-03-05T22:24:57.393231', 5433, 601),
       ('66620d098179f92e55960ef7', '66620d098179f92e55960f1e', 4, '66620d098179f92e55960f56',
        '2024-03-05T22:24:57.393231', 5433, 941),
       ('66620d098179f92e55960ef7', '66620d098179f92e55960f1f', 4, '66620d098179f92e55960f56',
        '2024-03-05T22:24:57.393231', 5433, 506),
       ('66620d098179f92e55960ef8', '66620d098179f92e55960f23', 4, '66620d098179f92e55960f57',
        '2024-04-08T22:24:57.393259', 6553, 38),
       ('66620d098179f92e55960ef8', '66620d098179f92e55960f1f', 4, '66620d098179f92e55960f57',
        '2024-04-08T22:24:57.393259', 6553, 967),
       ('66620d098179f92e55960ef8', '66620d098179f92e55960f22', 4, '66620d098179f92e55960f57',
        '2024-04-08T22:24:57.393259', 6553, 691),
       ('66620d098179f92e55960ef8', '66620d098179f92e55960f1e', 4, '66620d098179f92e55960f57',
        '2024-04-08T22:24:57.393259', 6553, 655),
       ('66620d098179f92e55960ef9', '66620d098179f92e55960f26', 3, '66620d098179f92e55960f58',
        '2024-05-08T22:24:57.393286', 4098, 936),
       ('66620d098179f92e55960ef9', '66620d098179f92e55960f21', 3, '66620d098179f92e55960f58',
        '2024-05-08T22:24:57.393286', 4098, 611),
       ('66620d098179f92e55960ef9', '66620d098179f92e55960f23', 3, '66620d098179f92e55960f58',
        '2024-05-08T22:24:57.393286', 4098, 86),
       ('66620d098179f92e55960efa', '66620d098179f92e55960f24', 3, '66620d098179f92e55960f59',
        '2024-03-08T22:24:57.393350', 4577, 912),
       ('66620d098179f92e55960efa', '66620d098179f92e55960f27', 3, '66620d098179f92e55960f59',
        '2024-03-08T22:24:57.393350', 4577, 377),
       ('66620d098179f92e55960efa', '66620d098179f92e55960f23', 3, '66620d098179f92e55960f59',
        '2024-03-08T22:24:57.393350', 4577, 760),
       ('66620d098179f92e55960efb', '66620d098179f92e55960f26', 4, '66620d098179f92e55960f5a',
        '2024-05-30T22:24:57.393375', 7338, 228),
       ('66620d098179f92e55960efb', '66620d098179f92e55960f22', 4, '66620d098179f92e55960f5a',
        '2024-05-30T22:24:57.393375', 7338, 778),
       ('66620d098179f92e55960efb', '66620d098179f92e55960f23', 4, '66620d098179f92e55960f5a',
        '2024-05-30T22:24:57.393375', 7338, 345),
       ('66620d098179f92e55960efb', '66620d098179f92e55960f1e', 4, '66620d098179f92e55960f5a',
        '2024-05-30T22:24:57.393375', 7338, 83),
       ('66620d098179f92e55960efc', '66620d098179f92e55960f25', 3, '66620d098179f92e55960f5b',
        '2024-03-04T22:24:57.393403', 3817, 255),
       ('66620d098179f92e55960efc', '66620d098179f92e55960f1f', 3, '66620d098179f92e55960f5b',
        '2024-03-04T22:24:57.393403', 3817, 631),
       ('66620d098179f92e55960efc', '66620d098179f92e55960f1e', 3, '66620d098179f92e55960f5b',
        '2024-03-04T22:24:57.393403', 3817, 791),
       ('66620d098179f92e55960efd', '66620d098179f92e55960f26', 3, '66620d098179f92e55960f5c',
        '2024-03-17T22:24:57.393425', 2596, 705),
       ('66620d098179f92e55960efd', '66620d098179f92e55960f21', 3, '66620d098179f92e55960f5c',
        '2024-03-17T22:24:57.393425', 2596, 405),
       ('66620d098179f92e55960efd', '66620d098179f92e55960f20', 3, '66620d098179f92e55960f5c',
        '2024-03-17T22:24:57.393425', 2596, 817),
       ('66620d098179f92e55960efe', '66620d098179f92e55960f24', 4, '66620d098179f92e55960f5d',
        '2024-05-15T22:24:57.393452', 4119, 135),
       ('66620d098179f92e55960efe', '66620d098179f92e55960f24', 4, '66620d098179f92e55960f5d',
        '2024-05-15T22:24:57.393452', 4119, 746),
       ('66620d098179f92e55960efe', '66620d098179f92e55960f26', 4, '66620d098179f92e55960f5d',
        '2024-05-15T22:24:57.393452', 4119, 232),
       ('66620d098179f92e55960efe', '66620d098179f92e55960f21', 4, '66620d098179f92e55960f5d',
        '2024-05-15T22:24:57.393452', 4119, 339),
       ('66620d098179f92e55960eff', '66620d098179f92e55960f23', 3, '66620d098179f92e55960f5e',
        '2024-03-11T22:24:57.393482', 4078, 122),
       ('66620d098179f92e55960eff', '66620d098179f92e55960f20', 3, '66620d098179f92e55960f5e',
        '2024-03-11T22:24:57.393482', 4078, 369),
       ('66620d098179f92e55960eff', '66620d098179f92e55960f1e', 3, '66620d098179f92e55960f5e',
        '2024-03-11T22:24:57.393482', 4078, 75),
       ('66620d098179f92e55960ef6', '66620d098179f92e55960f2c', 2, '66620d098179f92e55960f5f',
        '2024-05-24T22:24:57.393508', 5437, 261),
       ('66620d098179f92e55960ef6', '66620d098179f92e55960f2a', 2, '66620d098179f92e55960f5f',
        '2024-05-24T22:24:57.393508', 5437, 88),
       ('66620d098179f92e55960ef7', '66620d098179f92e55960f28', 2, '66620d098179f92e55960f60',
        '2024-05-29T22:24:57.393533', 2222, 901),
       ('66620d098179f92e55960ef7', '66620d098179f92e55960f28', 2, '66620d098179f92e55960f60',
        '2024-05-29T22:24:57.393533', 2222, 352),
       ('66620d098179f92e55960ef8', '66620d098179f92e55960f2e', 3, '66620d098179f92e55960f61',
        '2024-04-10T22:24:57.393555', 3978, 454),
       ('66620d098179f92e55960ef8', '66620d098179f92e55960f29', 3, '66620d098179f92e55960f61',
        '2024-04-10T22:24:57.393555', 3978, 926),
       ('66620d098179f92e55960ef8', '66620d098179f92e55960f2d', 3, '66620d098179f92e55960f61',
        '2024-04-10T22:24:57.393555', 3978, 281),
       ('66620d098179f92e55960ef9', '66620d098179f92e55960f30', 4, '66620d098179f92e55960f62',
        '2024-03-18T22:24:57.393575', 5531, 454),
       ('66620d098179f92e55960ef9', '66620d098179f92e55960f29', 4, '66620d098179f92e55960f62',
        '2024-03-18T22:24:57.393575', 5531, 561),
       ('66620d098179f92e55960ef9', '66620d098179f92e55960f2b', 4, '66620d098179f92e55960f62',
        '2024-03-18T22:24:57.393575', 5531, 476),
       ('66620d098179f92e55960ef9', '66620d098179f92e55960f28', 4, '66620d098179f92e55960f62',
        '2024-03-18T22:24:57.393575', 5531, 828),
       ('66620d098179f92e55960efa', '66620d098179f92e55960f28', 5, '66620d098179f92e55960f63',
        '2024-04-13T22:24:57.393604', 7934, 418),
       ('66620d098179f92e55960efa', '66620d098179f92e55960f2b', 5, '66620d098179f92e55960f63',
        '2024-04-13T22:24:57.393604', 7934, 381),
       ('66620d098179f92e55960efa', '66620d098179f92e55960f30', 5, '66620d098179f92e55960f63',
        '2024-04-13T22:24:57.393604', 7934, 43),
       ('66620d098179f92e55960efa', '66620d098179f92e55960f31', 5, '66620d098179f92e55960f63',
        '2024-04-13T22:24:57.393604', 7934, 231),
       ('66620d098179f92e55960efa', '66620d098179f92e55960f2d', 5, '66620d098179f92e55960f63',
        '2024-04-13T22:24:57.393604', 7934, 176),
       ('66620d098179f92e55960efb', '66620d098179f92e55960f29', 4, '66620d098179f92e55960f64',
        '2024-05-12T22:24:57.393631', 7608, 807),
       ('66620d098179f92e55960efb', '66620d098179f92e55960f2a', 4, '66620d098179f92e55960f64',
        '2024-05-12T22:24:57.393631', 7608, 184),
       ('66620d098179f92e55960efb', '66620d098179f92e55960f2f', 4, '66620d098179f92e55960f64',
        '2024-05-12T22:24:57.393631', 7608, 283),
       ('66620d098179f92e55960efb', '66620d098179f92e55960f30', 4, '66620d098179f92e55960f64',
        '2024-05-12T22:24:57.393631', 7608, 538),
       ('66620d098179f92e55960efc', '66620d098179f92e55960f28', 2, '66620d098179f92e55960f65',
        '2024-04-06T22:24:57.393658', 3858, 764),
       ('66620d098179f92e55960efc', '66620d098179f92e55960f2a', 2, '66620d098179f92e55960f65',
        '2024-04-06T22:24:57.393658', 3858, 514),
       ('66620d098179f92e55960efd', '66620d098179f92e55960f28', 3, '66620d098179f92e55960f66',
        '2024-04-20T22:24:57.393683', 2686, 810),
       ('66620d098179f92e55960efd', '66620d098179f92e55960f29', 3, '66620d098179f92e55960f66',
        '2024-04-20T22:24:57.393683', 2686, 160),
       ('66620d098179f92e55960efd', '66620d098179f92e55960f2e', 3, '66620d098179f92e55960f66',
        '2024-04-20T22:24:57.393683', 2686, 963),
       ('66620d098179f92e55960efe', '66620d098179f92e55960f28', 3, '66620d098179f92e55960f67',
        '2024-05-17T22:24:57.393762', 2686, 894),
       ('66620d098179f92e55960efe', '66620d098179f92e55960f2e', 3, '66620d098179f92e55960f67',
        '2024-05-17T22:24:57.393762', 2686, 689),
       ('66620d098179f92e55960efe', '66620d098179f92e55960f31', 3, '66620d098179f92e55960f67',
        '2024-05-17T22:24:57.393762', 2686, 803),
       ('66620d098179f92e55960eff', '66620d098179f92e55960f2e', 2, '66620d098179f92e55960f68',
        '2024-04-06T22:24:57.393805', 1575, 613),
       ('66620d098179f92e55960eff', '66620d098179f92e55960f29', 2, '66620d098179f92e55960f68',
        '2024-04-06T22:24:57.393805', 1575, 527);

