export interface User {
    email: string;
    password: string | null;
    nome: string;
    cognome: string;
    data_nascita: string;
}

export interface UserData {
    id: number;
    email: string;
    password: string;
    nome: string;
    cognome: string;
    data_nascita: string;
    exp: string;
    id_scuola: string | null;
    indirizzo_di_studio: string | null;
    descrizione_docente: string | null;
    immagine_profilo: string | null;
    link_pagina_docente: string | null;
    roles: string[];
}

export interface Course {
    id: number;
    titolo: string;
    descrizione: string | null;
    lingua: string | null;
    immagine_copertina: any | null;
    file_certificato: any | null;
    abilitato: boolean;
}

export interface ProgCourse {
    id: number;
    modalita: string;
    limite_iscrizioni: number | null;
    password_certificato: string;
    id_corso: number;
    lezioni: Lesson[] | undefined;
    iscritti: any[] | undefined;
}

export interface Lesson {
    id: number;
    data: string;
    orario_inizio: string;
    orario_fine: string;
    link_stanza_virtuale: string | null;
    passcode_stanza_virtuale: string | null;
    codice_verifica_presenza: string;
    id_aula: number | null;
    aula: Aula | undefined;
    id_programmazione_corso: number;
}

export interface Aula {
    id: number;
    nome: string;
    edificio: string;
    campus: string;
    capienza: string;
}