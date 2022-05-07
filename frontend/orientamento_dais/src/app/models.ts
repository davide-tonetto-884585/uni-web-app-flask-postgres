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
    immagine_copertina: string | null;
    file_certificato: string | null;
    abilitato: boolean;
}