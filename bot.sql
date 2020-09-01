--
-- PostgreSQL database dump
--

-- Dumped from database version 11.7
-- Dumped by pg_dump version 11.7

-- Started on 2020-09-02 00:17:13 MSK

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 4 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;

--
-- TOC entry 3157 (class 0 OID 0)
-- Dependencies: 4
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- TOC entry 609 (class 1247 OID 16444)
-- Name: pos; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.pos AS ENUM (
    'OPEN',
    'CLOSED',
    'ERROR',
    'NOT_ENOUGH_FUNDS',
    'SPIKE'
);


ALTER TYPE public.pos OWNER TO postgres;

--
-- TOC entry 593 (class 1247 OID 16394)
-- Name: side; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.side AS ENUM (
    'SELL',
    'BUY'
);


ALTER TYPE public.side OWNER TO postgres;

--
-- TOC entry 599 (class 1247 OID 16410)
-- Name: status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.status AS ENUM (
    'NEW',
    'FILLED',
    'ERROR',
    'EXPIRED'
);


ALTER TYPE public.status OWNER TO postgres;

--
-- TOC entry 596 (class 1247 OID 16400)
-- Name: type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.type AS ENUM (
    'EXEC_STARTED',
    'MARKET',
    'LIMIT_MAKER',
    'STOP_LOSS_LIMIT',
    'LIMIT'
);


ALTER TYPE public.type OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 198 (class 1259 OID 16417)
-- Name: initial_order; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.initial_order (
    id bigint NOT NULL,
    side public.side NOT NULL,
    status public.status NOT NULL,
    pair character varying(10) NOT NULL,
    qty numeric NOT NULL,
    price numeric NOT NULL,
    raworder text,
    commission numeric,
    commission_asset character(6),
    cummulative_quote_qty numeric,
    type public.type NOT NULL,
    "position" public.pos NOT NULL,
    order_id bigint NOT NULL,
    transact_time timestamp without time zone NOT NULL
);


ALTER TABLE public.initial_order OWNER TO postgres;

--
-- TOC entry 197 (class 1259 OID 16415)
-- Name: inital_order_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.initial_order ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.inital_order_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 200 (class 1259 OID 16435)
-- Name: martingale_order; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.martingale_order (
    id bigint NOT NULL,
    initial_order_id bigint NOT NULL,
    order_id bigint NOT NULL,
    side public.side NOT NULL,
    status public.status NOT NULL,
    pair character varying(10) NOT NULL,
    qty numeric NOT NULL,
    price numeric NOT NULL,
    raworder text,
    commission numeric,
    commission_asset character(6),
    cummulative_quote_qty numeric,
    type public.type NOT NULL,
    transact_time timestamp with time zone NOT NULL
);


ALTER TABLE public.martingale_order OWNER TO postgres;

--
-- TOC entry 199 (class 1259 OID 16433)
-- Name: martin_order_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.martingale_order ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.martin_order_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 3149 (class 0 OID 16417)
-- Dependencies: 198
-- Data for Name: initial_order; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.initial_order (id, side, status, pair, qty, price, raworder, commission, commission_asset, cummulative_quote_qty, type, "position", order_id, transact_time) FROM stdin;
15	SELL	FILLED	ADABNB	25.00000000	0.00464400	[{"price": "0.00464400", "qty": "25.00000000", "commission": "0.00008707", "commissionAsset": "BNB", "tradeId": 2460364}]	0.00008707	BNB   	0.11610000	MARKET	ERROR	47752824	2020-06-02 02:05:09
17	BUY	FILLED	BRDBNB	20.00000000	0.00653000	[{"price": "0.00653000", "qty": "20.00000000", "commission": "0.00009823", "commissionAsset": "BNB", "tradeId": 534955}]	0.00009823	BNB   	0.13060000	MARKET	CLOSED	22133208	2020-06-09 00:32:47
22	BUY	FILLED	BRDBNB	20.00000000	0.00744000	[{"price": "0.00744000", "qty": "20.00000000", "commission": "0.00011142", "commissionAsset": "BNB", "tradeId": 547007}]	0.00011142	BNB   	0.14880000	MARKET	CLOSED	22391666	2020-06-17 17:51:16
20	BUY	FILLED	BRDBNB	20.00000000	0.00715000	[{"price": "0.00715000", "qty": "20.00000000", "commission": "0.00010731", "commissionAsset": "BNB", "tradeId": 537323}]	0.00010731	BNB   	0.14300000	MARKET	SPIKE	22183762	2020-06-10 12:41:02
18	SELL	FILLED	BNBBTC	0.10000000	0.00178640	[{"price": "0.00178640", "qty": "0.10000000", "commission": "0.00007560", "commissionAsset": "BNB", "tradeId": 79344872}]	0.00007560	BNB   	0.00017864	MARKET	CLOSED	397972028	2020-06-09 14:40:57
21	BUY	FILLED	BRDBNB	20.00000000	0.00732940	[{"price": "0.00731000", "qty": "0.30000000", "commission": "0.00000163", "commissionAsset": "BNB", "tradeId": 545995}, {"price": "0.00732000", "qty": "0.60000000", "commission": "0.00000327", "commissionAsset": "BNB", "tradeId": 545996}, {"price": "0.00733000", "qty": "19.10000000", "commission": "0.00010433", "commissionAsset": "BNB", "tradeId": 545997}]	0.00010923	BNB   	0.14658800	MARKET	CLOSED	22365291	2020-06-16 17:05:48
24	BUY	FILLED	BRDBNB	20.00000000	0.00869000	[{"price": "0.00869000", "qty": "20.00000000", "commission": "0.00012989", "commissionAsset": "BNB", "tradeId": 551559}]	0.00012989	BNB   	0.17380000	MARKET	CLOSED	22493554	2020-06-20 13:26:10
23	BUY	FILLED	ADABNB	30.00000000	0.00503100	[{"price": "0.00503100", "qty": "30.00000000", "commission": "0.00011319", "commissionAsset": "BNB", "tradeId": 2521255}]	0.00011319	BNB   	0.15093000	MARKET	CLOSED	49290729	2020-06-17 21:53:45
25	SELL	FILLED	BRDBNB	20.00000000	0.00788000	[{"price": "0.00788000", "qty": "20.00000000", "commission": "0.00011820", "commissionAsset": "BNB", "tradeId": 554339}]	0.00011820	BNB   	0.15760000	MARKET	CLOSED	22556707	2020-06-22 21:17:54
26	BUY	FILLED	BRDBNB	20.00000000	0.00800990	[{"price": "0.00800000", "qty": "0.20000000", "commission": "0.00000119", "commissionAsset": "BNB", "tradeId": 556341}, {"price": "0.00801000", "qty": "19.80000000", "commission": "0.00011846", "commissionAsset": "BNB", "tradeId": 556342}]	0.00011965	BNB   	0.16019800	MARKET	ERROR	22599128	2020-06-24 22:53:20
27	BUY	FILLED	BRDBNB	20.00000000	0.00798000	[{"price": "0.00798000", "qty": "20.00000000", "commission": "0.00011898", "commissionAsset": "BNB", "tradeId": 556349}]	0.00011898	BNB   	0.15960000	MARKET	ERROR	22599487	2020-06-25 00:51:23
\.


--
-- TOC entry 3151 (class 0 OID 16435)
-- Dependencies: 200
-- Data for Name: martingale_order; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.martingale_order (id, initial_order_id, order_id, side, status, pair, qty, price, raworder, commission, commission_asset, cummulative_quote_qty, type, transact_time) FROM stdin;
1	47752824	47752850	BUY	ERROR	ADABNB	50.00000000	0.00450500	[]	0.00000000	      	0.00000000	LIMIT	2020-06-02 02:05:12+03
2	47752824	47752853	SELL	ERROR	ADABNB	1.00000000	0.00487600	[]	0.00000000	      	0.00000000	LIMIT	2020-06-02 02:05:14+03
3	22133208	22133209	SELL	FILLED	BRDBNB	20.00000000	0.00673000		0	      	0	LIMIT	2020-06-09 00:32:49+03
4	22133208	22133210	BUY	EXPIRED	BRDBNB	40.0	0.00620000	[]	0.00000000	      	0.00000000	LIMIT	2020-06-09 00:32:50+03
8	22183762	22183763	SELL	EXPIRED	BRDBNB	20.0	0.00736000	[]	0.00000000	      	0.00000000	LIMIT	2020-06-10 12:41:08+03
9	22183762	22183765	BUY	FILLED	BRDBNB	40.00000000	0.00679000		0	      	0	LIMIT	2020-06-10 12:41:08+03
10	22183762	22213700	SELL	FILLED	BRDBNB	60.0	0.00699000	[]	0.00000000	      	0.00000000	LIMIT	2020-06-11 14:15:19+03
5	397972028	397972039	BUY	FILLED	BNBBTC	0.10000000	0.00173280		0	      	0	LIMIT	2020-06-09 14:41:01+03
6	397972028	397972041	SELL	EXPIRED	BNBBTC	0.2	0.00187570	[]	0.00000000	      	0.00000000	LIMIT	2020-06-09 14:41:01+03
11	22365291	22365292	SELL	FILLED	BRDBNB	20.00000000	0.00755000		0	      	0	LIMIT	2020-06-16 17:05:53+03
12	22365291	22365293	BUY	EXPIRED	BRDBNB	40.0	0.00696000	[]	0.00000000	      	0.00000000	LIMIT	2020-06-16 17:05:53+03
13	22391666	22391667	SELL	FILLED	BRDBNB	20.00000000	0.00766000		0	      	0	LIMIT	2020-06-17 17:51:20+03
14	22391666	22391669	BUY	EXPIRED	BRDBNB	40.0	0.00707000	[]	0.00000000	      	0.00000000	LIMIT	2020-06-17 17:51:20+03
17	22493554	22493557	SELL	FILLED	BRDBNB	20.0	0.00895000	[]	0.00000000	      	0.00000000	LIMIT	2020-06-20 13:26:14+03
15	49290729	49290733	SELL	FILLED	ADABNB	30.00000000	0.00518200		0	      	0	LIMIT	2020-06-17 21:53:50+03
16	49290729	49290734	BUY	EXPIRED	ADABNB	60.0	0.00477900	[]	0.00000000	      	0.00000000	LIMIT	2020-06-17 21:53:50+03
18	22556707	22556709	BUY	FILLED	BRDBNB	20.00000000	0.00764000		0	      	0	LIMIT	2020-06-22 21:18:03+03
19	22599128	22599132	SELL	EXPIRED	BRDBNB	20.0	0.00825000	[]	0.00000000	      	0.00000000	LIMIT	2020-06-24 22:53:30+03
20	22599128	22599133	BUY	FILLED	BRDBNB	40.00000000	0.00761000		0	      	0	LIMIT	2020-06-24 22:53:32+03
22	22599128	22687846	SELL	ERROR	BRDBNB	60.0	0.00798000	[]	0.00000000	      	0.00000000	LIMIT	2020-06-28 23:46:42+03
21	22599487	22599491	SELL	ERROR	BRDBNB	20.0	0.00822000	[]	0.00000000	      	0.00000000	LIMIT	2020-06-25 00:51:33+03
\.


--
-- TOC entry 3158 (class 0 OID 0)
-- Dependencies: 197
-- Name: inital_order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inital_order_id_seq', 27, true);


--
-- TOC entry 3159 (class 0 OID 0)
-- Dependencies: 199
-- Name: martin_order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.martin_order_id_seq', 22, true);


--
-- TOC entry 3024 (class 2606 OID 16421)
-- Name: initial_order initial_order_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.initial_order
    ADD CONSTRAINT initial_order_pkey PRIMARY KEY (id);


--
-- TOC entry 3026 (class 2606 OID 16442)
-- Name: martingale_order martin_order_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.martingale_order
    ADD CONSTRAINT martin_order_pkey PRIMARY KEY (id);


-- Completed on 2020-09-02 00:17:13 MSK

--
-- PostgreSQL database dump complete
--

