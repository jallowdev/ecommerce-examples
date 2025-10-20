-- python manage.py createsuperuser --email admin@example.com --username admin
-- 321//System
insert into users_role (code, name, status) values('ADMIN_SYSTEM', 'Super Admin','ENABLE');
insert into users_role (code, name, status) values('SUPERVISOR_SYSTEM', 'Superviseur System','ENABLE');
insert into users_role (code, name, status) values('TRESORIER_SYSTEM', 'Tresorier System','ENABLE');
insert into users_role (code, name, status) values('SUPPORT_SYSTEM', 'Support System','ENABLE');

insert into users_role (code, name, status) values('ADMIN_MAGASIN', 'Administrateur Magasin','ENABLE');
insert into users_role (code, name, status) values('CHEF_BOUTIQUE', 'Chef Boutique','ENABLE');
insert into users_role (code, name, status) values('SUPERVISOR', 'Superviseur','ENABLE');
insert into users_role (code, name, status) values('AGENT_CAISSE', 'Agent Caisse','ENABLE');
insert into users_role (code, name, status) values('AGENT_CONTROLE', 'Agent Controler','ENABLE');
insert into users_role (code, name, status) values('SUPPORT', 'Support Client','ENABLE');

insert into users_role (code, name, status) values('CUSTOMER', 'Client','ENABLE');
insert into users_role (code, name, status) values('CUSTOMER_INVOICE', 'Client Magasin','ENABLE');

-- FUNCTIONALITY

insert into users_functionality (code, libelle, icon, url,orderby,status) values('HOME', 'Tableau', 'home','home', 1,'ENABLE');
insert into users_functionality (code, libelle, icon, url,orderby,status,parent_id) values('DASHBOARD', 'Dashboard', 'home','home', 1,'ENABLE','HOME');

insert into users_functionality (code, libelle, icon, url,orderby,status) values('ENTITIES', 'Entités', '','entities', 2,'ENABLE');
insert into users_functionality (code, libelle, icon, url,orderby,status,parent_id) values('ENTITY', 'Entités', '','entities', 3,'ENABLE','ENTITIES');
insert into users_functionality (code, libelle, icon, url,orderby,status,parent_id) values('USERS', 'Utilisateurs', '','users', 4,'ENABLE','ENTITIES');
insert into users_functionality (code, libelle, icon, url,orderby,status,parent_id) values('CUSTOMERS', 'Compte Clients', '','customers', 5,'DISABLE','ENTITIES');

insert into users_functionality (code, libelle, icon, url,orderby,status,parent_id) values('STOCKS', 'Stocks', '','stocks', 6,'ENABLE',null);
insert into users_functionality (code, libelle, icon, url,orderby,status,parent_id) values('PRODUCTS', 'Produits', 'box','products', 7,'ENABLE','STOCKS');
insert into users_functionality (code, libelle, icon, url,orderby,status,parent_id) values('CATEGORIES', 'Categories', 'codepen','categories', 8,'ENABLE','STOCKS');
insert into users_functionality (code, libelle, icon, url,orderby,status,parent_id) values('BRANDS', 'Marques', 'tag','brands', 9,'ENABLE','STOCKS');
insert into users_functionality (code, libelle, icon, url,orderby,status,parent_id) values('UNITIES', 'Unités', 'speaker','unities', 10,'ENABLE','STOCKS');

insert into users_functionality (code, libelle, icon, url,orderby,status,parent_id) values('SALES', 'Ventes', '','', 1,'ENABLE');
insert into users_functionality (code, libelle, icon, url,orderby,status,parent_id) values('PURCHASES', 'Achats', '','', 1,'ENABLE');
insert into users_functionality (code, libelle, icon, url,orderby,status,parent_id) values('MARKETING', 'Communications', '','', 1,'ENABLE');
insert into users_functionality (code, libelle, icon, url,orderby,status,parent_id) values('SETTINGS', 'Parametrages', '','', 1,'ENABLE');

-- ROLE - FUNCTIONALITIES

INSERT INTO users_functionality_roles(id, functionality_id, role_id)VALUES (10, 'DASHBOARD', 'ADMIN_SYSTEM');
INSERT INTO users_functionality_roles(id, functionality_id, role_id)VALUES (11, 'ENTITIES', 'ADMIN_SYSTEM');
INSERT INTO users_functionality_roles(id, functionality_id, role_id)VALUES (12, 'ENTITY', 'ADMIN_SYSTEM');
INSERT INTO users_functionality_roles(id, functionality_id, role_id)VALUES (13, 'USERS', 'ADMIN_SYSTEM');
INSERT INTO users_functionality_roles(id, functionality_id, role_id)VALUES (14, 'CUSTOMERS', 'ADMIN_SYSTEM');
INSERT INTO users_functionality_roles(id, functionality_id, role_id)VALUES (15, 'STOCKS', 'ADMIN_SYSTEM');
INSERT INTO users_functionality_roles(id, functionality_id, role_id)VALUES (16, 'PRODUCTS', 'ADMIN_SYSTEM');
INSERT INTO users_functionality_roles(id, functionality_id, role_id)VALUES (17, 'CATEGORIES', 'ADMIN_SYSTEM');
INSERT INTO users_functionality_roles(id, functionality_id, role_id)VALUES (18, 'BRANDS', 'ADMIN_SYSTEM');
INSERT INTO users_functionality_roles(id, functionality_id, role_id)VALUES (19, 'UNITIES', 'ADMIN_SYSTEM');




--- ENTITY
insert into users_entity(id, identity, title, subtitle, entitytype, status,parent_id,created_at,updated_at,slug)
	VALUES (1,'001', 'OUDIA PLATEFORME', 'OUDIA PLATEFORME', 'RACINE','ENABLE',NULL,'2025-01-15 19:30:31.566188+00', '2025-01-15 19:30:31.566188+00','');
insert into users_entity(id, identity, title, subtitle, entitytype, status,parent_id,created_at,updated_at,slug)
	VALUES (2,'002', 'OUDIA PARTENAIRE', 'OUDIA PARTENAIRE', 'PARTNER','ENABLE',1,'2025-01-15 19:30:31.566188+00', '2025-01-15 19:30:31.566188+00','');
insert into users_entity(id, identity, title, subtitle, entitytype, status,parent_id,created_at,updated_at,slug)
	VALUES (3,'003', 'OUDIA BOUTIQUE', 'OUDIA SERVICE', 'BOUTIQUE','ENABLE',2,'2025-01-15 19:30:31.566188+00', '2025-01-15 19:30:31.566188+00','');

-- UNITES
insert into stocks_unity(id, identity, name, code, slug, status,created_at, updated_at)
	VALUES (1, '001', 'Kilogramme', 'KG', '', 'ENABLE', '2025-01-15 19:30:31.566188+00', '2025-01-15 19:30:31.566188+00');
insert into stocks_unity(id, identity, name, code, slug, status,created_at, updated_at)
	VALUES (2, '002', 'Gramme', 'G', '', 'ENABLE', '2025-01-15 19:30:31.566188+00', '2025-01-15 19:30:31.566188+00');
insert into stocks_unity(id, identity, name, code, slug, status,created_at, updated_at)
	VALUES (3, '003', 'Mettre', 'M', '', 'ENABLE', '2025-01-15 19:30:31.566188+00', '2025-01-15 19:30:31.566188+00');
insert into stocks_unity(id, identity, name, code, slug, status,created_at, updated_at)
	VALUES (4, '004', 'Tonne', 'T', '', 'ENABLE', '2025-01-15 19:30:31.566188+00', '2025-01-15 19:30:31.566188+00');
insert into stocks_unity(id, identity, name, code, slug, status,created_at, updated_at)
	VALUES (5, '005', 'Piece', 'PC', '', 'ENABLE', '2025-01-15 19:30:31.566188+00', '2025-01-15 19:30:31.566188+00');
insert into stocks_unity(id, identity, name, code, slug, status,created_at, updated_at)
	VALUES (6, '006', 'Litre', 'L', '', 'ENABLE', '2025-01-15 19:30:31.566188+00', '2025-01-15 19:30:31.566188+00');
insert into stocks_unity(id, identity, name, code, slug, status,created_at, updated_at)
	VALUES (7, '007', 'Cartone', 'CR', '', 'ENABLE', '2025-01-15 19:30:31.566188+00', '2025-01-15 19:30:31.566188+00');
insert into stocks_unity(id, identity, name, code, slug, status,created_at, updated_at)
	VALUES (8, '008', 'Douzaine', '12D', '', 'ENABLE', '2025-01-15 19:30:31.566188+00', '2025-01-15 19:30:31.566188+00');

-- payment
insert into invoices_payment(id, name, code, icon, status) VALUES (10, 'Espece', 'CASH', '', 'ENABLE');
insert into invoices_payment(id, name, code, icon, status) VALUES (11, 'Wave', 'WAVE', '', 'ENABLE');
insert into invoices_payment(id, name, code, icon, status) VALUES (12, 'Orange money', 'ORANGEMONEY', '', 'ENABLE');
insert into invoices_payment(id, name, code, icon, status) VALUES (13, 'Carte Bancaire', 'BANKCARD', '', 'ENABLE');

-- CATEGORY
INSERT INTO stocks_category(id, code,categoryType,name,status)VALUES (1, '001','CATEGORY','Ordinateur', 'ENABLE');
INSERT INTO stocks_category(id, code,categoryType,name,status)VALUES (2, '002','CATEGORY','Television', 'ENABLE');
INSERT INTO stocks_category(id, code,categoryType,name,status)VALUES (3, '003','CATEGORY','Telephone', 'ENABLE');
INSERT INTO stocks_category(id, code,categoryType,name,status)VALUES (4, '004','CATEGORY','Alimentation', 'ENABLE');
INSERT INTO stocks_category(id, code,categoryType,name,status)VALUES (5, '005','CATEGORY','Medicament', 'ENABLE');
INSERT INTO stocks_category(id, code,categoryType,name,status)VALUES (6, '006','CATEGORY','Electromanager', 'ENABLE');

-- ADDRESS
insert into users_profile(
	id, phone, "kycDocType", "profileLink", "facebookLink", "instagramLink", "rectoLink", "versoLink", "selfieLink", "passportLink", gender)
	VALUES (1, '770000000', '', '', '', '', '', '', '', '', '');
insert into users_address(id, country, city, state, street, location, longitude, latitude) VALUES (1, 'SENEGAL', 'DAKAR','DAKAR','DAKAR', '','','');

--- user account

insert into users_useraccount(
	id, identity, address_id, entity_id, profile_id, role_id, user_id, "isConfirmed", status,created_at, updated_at)
	VALUES (1, '001', 1, 1, 2, 'ADMIN_SYSTEM', 1, TRUE, 'ENABLE', '2025-01-15 19:30:31.566188+00', '2025-01-15 19:30:31.566188+00');
