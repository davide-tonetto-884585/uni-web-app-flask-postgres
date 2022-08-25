import { Component, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { AulaHttpService } from '../aula-http.service';
import { CourseHttpService } from '../course-http.service';
import { MessageDialogComponent } from '../message-dialog/message-dialog.component';
import { Aula, Lesson, ProgCourse } from '../models';
import { UserHttpService } from '../user-http.service';
import { SECRET, FRONTEND_URL } from '../globals';
import * as CryptoJS from 'crypto-js';

@Component({
  selector: 'app-course-schedule-item',
  templateUrl: './course-schedule-item.component.html',
  styleUrls: ['./course-schedule-item.component.css']
})
export class CourseScheduleItemComponent implements OnInit {
  @Input() prog: ProgCourse | undefined;
  @Input() docenti_corso: any[] = [];

  QRInfo: string | null = null;

  constructor(
    private course_http: CourseHttpService,
    private aula_http: AulaHttpService,
    private dialog: MatDialog,
    private user_http: UserHttpService,
  ) { }

  ngOnInit(): void {
    this.loadLessons();
  }

  getId(): number | undefined {
    return this.user_http.getId();
  }

  isLogged(): boolean {
    return this.user_http.isLogged();
  }

  isStudent(): boolean {
    return this.user_http.isStudent();
  }

  enrollStudent(in_presenza: boolean | null = null) {
    let id_stud = this.user_http.getId()
    if (id_stud && this.prog) {
      this.course_http.enrollStudent(this.prog.id_corso, this.prog.id, id_stud, in_presenza).subscribe({
        next: (d) => {
          this.dialog.open(MessageDialogComponent, {
            data: {
              text: 'Successful registration',
              title: 'Done!',
              error: false
            },
          });
        },
        error: (err) => {
          this.dialog.open(MessageDialogComponent, {
            data: {
              text: err,
              title: 'Failed!',
              error: true
            },
          });
        }
      })
    }
  }

  loadLessons(): void {
    if (this.prog) {
      this.course_http.getLezioniProgCorso(this.prog.id_corso, this.prog.id).subscribe({
        next: (lezioni: Lesson[]) => {
          if (this.prog) {
            this.prog.lezioni = lezioni;

            this.prog.lezioni.forEach((les: Lesson) => {
              if (les.id_aula) {
                this.aula_http.getAula(les.id_aula).subscribe({
                  next: (aula: Aula) => {
                    les.aula = aula;
                  }
                });
              }
            });
          }
        }
      });

      this.course_http.getIscrittiProgCorso(this.prog.id_corso, this.prog.id).subscribe({
        next: (iscritti) => {
          if (this.prog)
            this.prog.iscritti = iscritti;
        }
      })
    }
  }

  isProgInCorso(): boolean {
    return this.prog?.lezioni != undefined && this.prog.lezioni.length > 0 && this.prog.lezioni.every(les => new Date(les.data) >= new Date());
  }

  checkInscriptionLimit(): boolean {
    return !this.prog?.limite_iscrizioni || (this.prog?.iscritti != undefined && this.prog.iscritti.length < this.prog?.limite_iscrizioni);
  }

  isInscriptionLimitReached(): boolean {
    return this.prog != undefined && this.prog.limite_iscrizioni != null && this.prog.iscritti != undefined && this.prog.iscritti.length >= this.prog.limite_iscrizioni;
  }

  getFreeSetsCount(): number | undefined {
    if (this.prog?.limite_iscrizioni == null) return undefined;
    if (this.prog.iscritti) {
      return this.prog?.limite_iscrizioni - this.prog.iscritti.length;
    } else return undefined;
  }

  isCourseTeacher(): boolean {
    if (this.getId() == undefined) return false;
    else return this.docenti_corso.some(doc => doc.id === this.getId());
  }

  showQR(id_corso: number, id_prog_corso: number, id_lezione: number, passcode: string): void {
    this.QRInfo = `${FRONTEND_URL}/login?pres_code=${id_corso}.${id_prog_corso}.${id_lezione}.${CryptoJS.AES.encrypt(passcode, SECRET).toString()}`;
    console.log(this.QRInfo) //TODO: togliere
  }
}
