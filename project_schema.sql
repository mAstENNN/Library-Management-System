--
-- PostgreSQL database dump
--

-- Dumped from database version 16.1
-- Dumped by pg_dump version 16.1

-- Started on 2024-04-14 19:23:13

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 215 (class 1259 OID 98564)
-- Name: address; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.address (
    email character varying(30) NOT NULL,
    number integer NOT NULL,
    street character varying(30) NOT NULL,
    city character varying(30) NOT NULL,
    state character varying(30) NOT NULL,
    zip integer NOT NULL
);


ALTER TABLE public.address OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 98567)
-- Name: article; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.article (
    id integer NOT NULL,
    title character varying(30) NOT NULL,
    journal character varying(30),
    number integer,
    year integer,
    issue character varying(30)
);


ALTER TABLE public.article OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 98573)
-- Name: book; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.book (
    id integer NOT NULL,
    title character varying(30) NOT NULL,
    isbn character varying(30),
    edition character varying(30),
    pages integer,
    year integer
);


ALTER TABLE public.book OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 98576)
-- Name: borrows; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.borrows (
    email character varying(30) NOT NULL,
    id integer NOT NULL,
    borrow_date date NOT NULL,
    return_date date
);


ALTER TABLE public.borrows OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 98579)
-- Name: client; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.client (
    email character varying(50) NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(30) NOT NULL,
    overdue_fee numeric(8,2) DEFAULT 0 NOT NULL,
    password character varying(60)
);


ALTER TABLE public.client OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 98685)
-- Name: document_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.document_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.document_id_seq OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 98583)
-- Name: document; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.document (
    id integer DEFAULT nextval('public.document_id_seq'::regclass) NOT NULL,
    type character varying(30) NOT NULL,
    num_copies integer,
    publisher character varying(60)
);


ALTER TABLE public.document OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 98586)
-- Name: librarian; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.librarian (
    ssn character varying(11) NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(30) NOT NULL,
    email character varying(50) NOT NULL,
    salary numeric(8,2),
    password character varying(60)
);


ALTER TABLE public.librarian OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 98589)
-- Name: magazine; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.magazine (
    id integer NOT NULL,
    name character varying(30) NOT NULL,
    isbn character varying(30),
    month integer,
    year integer
);


ALTER TABLE public.magazine OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 98592)
-- Name: payment_method; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payment_method (
    email character varying(50) NOT NULL,
    card_number character varying(30) NOT NULL,
    number integer,
    street character varying(30),
    city character varying(30),
    state character varying(30),
    zip integer,
    "CVV" character varying(4),
    exp_date date,
    company character varying(30)
);


ALTER TABLE public.payment_method OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 98595)
-- Name: written_by; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.written_by (
    id integer NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(30) NOT NULL
);


ALTER TABLE public.written_by OWNER TO postgres;

--
-- TOC entry 4898 (class 0 OID 98564)
-- Dependencies: 215
-- Data for Name: address; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.address (email, number, street, city, state, zip) FROM stdin;
alex.johnson@example.com	444	aaaa	bbbb	dd	11111
\.


--
-- TOC entry 4899 (class 0 OID 98567)
-- Dependencies: 216
-- Data for Name: article; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.article (id, title, journal, number, year, issue) FROM stdin;
\.


--
-- TOC entry 4900 (class 0 OID 98573)
-- Dependencies: 217
-- Data for Name: book; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.book (id, title, isbn, edition, pages, year) FROM stdin;
\.


--
-- TOC entry 4901 (class 0 OID 98576)
-- Dependencies: 218
-- Data for Name: borrows; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.borrows (email, id, borrow_date, return_date) FROM stdin;
\.


--
-- TOC entry 4902 (class 0 OID 98579)
-- Dependencies: 219
-- Data for Name: client; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.client (email, first_name, last_name, overdue_fee, password) FROM stdin;
jane.smith@example.com	Jane	Smith	10.00	$2b$12$udxG7.6O5e07rTX0FS61g.b.RVylpz5uhGv8O9d2I5PZdzeIKx3he
alex.johnson@example.com	Alex	Johnson	4.00	$2b$12$mYS1XqusvKvkcK5eTkStleCFAN6et0hsVtn29Ag4GKikzRC5/UyPG
\.


--
-- TOC entry 4903 (class 0 OID 98583)
-- Dependencies: 220
-- Data for Name: document; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.document (id, type, num_copies, publisher) FROM stdin;
\.


--
-- TOC entry 4904 (class 0 OID 98586)
-- Dependencies: 221
-- Data for Name: librarian; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.librarian (ssn, first_name, last_name, email, salary, password) FROM stdin;
123-45-6789	John	Doe	john.doe@example.com	50000.00	$2b$12$udxG7.6O5e07rTX0FS61g.b.RVylpz5uhGv8O9d2I5PZdzeIKx3he
\.


--
-- TOC entry 4905 (class 0 OID 98589)
-- Dependencies: 222
-- Data for Name: magazine; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.magazine (id, name, isbn, month, year) FROM stdin;
\.


--
-- TOC entry 4906 (class 0 OID 98592)
-- Dependencies: 223
-- Data for Name: payment_method; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payment_method (email, card_number, number, street, city, state, zip, "CVV", exp_date, company) FROM stdin;
\.


--
-- TOC entry 4907 (class 0 OID 98595)
-- Dependencies: 224
-- Data for Name: written_by; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.written_by (id, first_name, last_name) FROM stdin;
\.


--
-- TOC entry 4914 (class 0 OID 0)
-- Dependencies: 225
-- Name: document_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.document_id_seq', 1, false);


--
-- TOC entry 4727 (class 2606 OID 98599)
-- Name: address address_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.address
    ADD CONSTRAINT address_pkey PRIMARY KEY (email, number, street, city, state, zip);


--
-- TOC entry 4729 (class 2606 OID 98601)
-- Name: article article_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.article
    ADD CONSTRAINT article_pkey PRIMARY KEY (id);


--
-- TOC entry 4731 (class 2606 OID 98605)
-- Name: book book_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.book
    ADD CONSTRAINT book_pkey PRIMARY KEY (id);


--
-- TOC entry 4733 (class 2606 OID 98607)
-- Name: borrows borrows_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.borrows
    ADD CONSTRAINT borrows_pkey PRIMARY KEY (email, id);


--
-- TOC entry 4735 (class 2606 OID 98609)
-- Name: client client_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client
    ADD CONSTRAINT client_pkey PRIMARY KEY (email);


--
-- TOC entry 4737 (class 2606 OID 98611)
-- Name: document document_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document
    ADD CONSTRAINT document_pkey PRIMARY KEY (id);


--
-- TOC entry 4739 (class 2606 OID 98613)
-- Name: librarian librarian_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.librarian
    ADD CONSTRAINT librarian_pkey PRIMARY KEY (ssn);


--
-- TOC entry 4741 (class 2606 OID 98615)
-- Name: magazine magazine_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.magazine
    ADD CONSTRAINT magazine_pkey PRIMARY KEY (id);


--
-- TOC entry 4743 (class 2606 OID 98617)
-- Name: payment_method payment_method_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_method
    ADD CONSTRAINT payment_method_pkey PRIMARY KEY (email, card_number);


--
-- TOC entry 4745 (class 2606 OID 98688)
-- Name: written_by written_by_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.written_by
    ADD CONSTRAINT written_by_pkey PRIMARY KEY (id, first_name, last_name);


--
-- TOC entry 4746 (class 2606 OID 98620)
-- Name: address address_email_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.address
    ADD CONSTRAINT address_email_fkey FOREIGN KEY (email) REFERENCES public.client(email) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 4747 (class 2606 OID 98625)
-- Name: article article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.article
    ADD CONSTRAINT article_id_fkey FOREIGN KEY (id) REFERENCES public.document(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 4748 (class 2606 OID 98630)
-- Name: book book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.book
    ADD CONSTRAINT book_id_fkey FOREIGN KEY (id) REFERENCES public.document(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 4749 (class 2606 OID 98635)
-- Name: borrows borrows_email_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.borrows
    ADD CONSTRAINT borrows_email_fkey FOREIGN KEY (email) REFERENCES public.client(email) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 4750 (class 2606 OID 98640)
-- Name: borrows borrows_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.borrows
    ADD CONSTRAINT borrows_id_fkey FOREIGN KEY (id) REFERENCES public.document(id) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;


--
-- TOC entry 4751 (class 2606 OID 98645)
-- Name: magazine magazine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.magazine
    ADD CONSTRAINT magazine_id_fkey FOREIGN KEY (id) REFERENCES public.document(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 4752 (class 2606 OID 98650)
-- Name: payment_method payment_method_email_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_method
    ADD CONSTRAINT payment_method_email_fkey FOREIGN KEY (email) REFERENCES public.client(email) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 4753 (class 2606 OID 98655)
-- Name: payment_method payment_method_email_number_street_city_state_zip_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_method
    ADD CONSTRAINT payment_method_email_number_street_city_state_zip_fkey FOREIGN KEY (email, number, street, city, state, zip) REFERENCES public.address(email, number, street, city, state, zip) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;


--
-- TOC entry 4754 (class 2606 OID 98665)
-- Name: written_by written_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.written_by
    ADD CONSTRAINT written_by_id_fkey FOREIGN KEY (id) REFERENCES public.document(id) ON UPDATE CASCADE ON DELETE CASCADE;


-- Completed on 2024-04-14 19:23:13

--
-- PostgreSQL database dump complete
--

