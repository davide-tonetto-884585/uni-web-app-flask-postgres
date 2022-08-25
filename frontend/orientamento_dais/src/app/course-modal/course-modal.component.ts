import { Component, OnInit, Inject } from '@angular/core';
import { MatDialog, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { CourseHttpService } from '../course-http.service';
import { AulaHttpService } from '../aula-http.service';

import { Course, ProgCourse, Lesson, Aula } from '../models';
import { Router } from '@angular/router';
import { MessageDialogComponent } from '../message-dialog/message-dialog.component';
import { UserHttpService } from '../user-http.service';
import { MatDateFormats, MAT_DATE_FORMATS, MAT_NATIVE_DATE_FORMATS } from '@angular/material/core';
import { MatDatepickerInputEvent } from '@angular/material/datepicker';

export const GRI_DATE_FORMATS: MatDateFormats = {
  ...MAT_NATIVE_DATE_FORMATS,
  display: {
    ...MAT_NATIVE_DATE_FORMATS.display,
    dateInput: {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    } as Intl.DateTimeFormatOptions,
  }
};

@Component({
  selector: 'app-course-modal',
  templateUrl: './course-modal.component.html',
  styleUrls: ['./course-modal.component.css'],
  providers: [
    { provide: MAT_DATE_FORMATS, useValue: GRI_DATE_FORMATS },
  ]
})
export class CourseModalComponent implements OnInit {
  progs: ProgCourse[] = [];
  aule: Aula[] = [];
  course: Course;
  isNew: boolean;

  immagine_copertina: any;
  file_certificato: any;

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: { isNew: boolean, course: Course },
    private user_http: UserHttpService,
    private course_http: CourseHttpService,
    private aula_http: AulaHttpService,
    public dialog: MatDialog
  ) {
    this.course = data.course;
    this.isNew = data.isNew;
  }

  ngOnInit(): void {
    if (this.course) {
      this.course_http.getProgrammazioniCorso(this.course.id, false).subscribe({
        next: (prog_corso: ProgCourse[]) => {
          this.progs = prog_corso;

          this.progs.forEach((el: ProgCourse) => {
            if (this.course) {
              this.course_http.getLezioniProgCorso(this.course.id, el.id).subscribe({
                next: (lezioni: Lesson[]) => {
                  el.lezioni = lezioni;

                  el.lezioni.forEach((les: Lesson) => {
                    if (les.id_aula) {
                      this.aula_http.getAula(les.id_aula).subscribe({
                        next: (aula: Aula) => {
                          les.aula = aula;
                        }
                      });
                    }
                  });
                }
              });
            }
          });
        }
      });

      this.aula_http.getAule().subscribe({
        next: (aule: Aula[]) => {
          this.aule = aule;
        }
      });
    }
  }

  addProgCorso(): void {
    this.progs.push({
      id: -1,
      modalita: '',
      limite_iscrizioni: null,
      password_certificato: '',
      id_corso: this.course?.id ?? -1,
      lezioni: [],
      iscritti: undefined
    });
  }

  addProgLesson(index: number): void {
    this.progs[index].lezioni?.push({
      id: -1,
      data: '',
      orario_inizio: '',
      orario_fine: '',
      link_stanza_virtuale: null,
      passcode_stanza_virtuale: null,
      codice_verifica_presenza: '',
      id_aula: null,
      aula: undefined,
      id_programmazione_corso: this.progs[index].id
    })
  }

  addCourse(): void {
    let user_id = this.user_http.getId() ?? -1;

    this.course_http.addCourse(this.course).subscribe({
      next: (d) => {
        this.course_http.addDocentiCorso(d.id_corso, [user_id]).subscribe({
          next: (d2) => {
            this.progs.forEach((prog) => {
              if (prog.id != -1) {
                this.course_http.updateProgCorso(d.id, prog).subscribe({
                  next: (d3) => {
                    if (prog.lezioni)
                      this.addLezioni(d.id, d3.id, prog.lezioni);
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
              } else {
                this.course_http.addProgCorso(this.course.id, prog).subscribe({
                  next: (d) => {
                    if (prog.lezioni)
                      this.addLezioni(this.course.id, d.id, prog.lezioni);
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
            })
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

  updateCourse(): void {
    this.course_http.updateCourse(this.course).subscribe({
      next: (d) => {
        if (this.progs.length === 0) this.dialog.closeAll();
        
        this.progs.forEach((prog) => {
          if (prog.id != -1) {
            this.course_http.updateProgCorso(this.course.id, prog).subscribe({
              next: (d) => {
                if (prog.lezioni)
                  this.addLezioni(this.course.id, prog.id, prog.lezioni);
                else
                  this.dialog.closeAll()
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
          } else {
            this.course_http.addProgCorso(this.course.id, prog).subscribe({
              next: (d) => {
                if (prog.lezioni)
                  this.addLezioni(this.course.id, d.id, prog.lezioni);
                else
                  this.dialog.closeAll()
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
        })
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

  addLezioni(id_corso: number, id_prog: number, lezioni: Lesson[]): void {
    lezioni.forEach((l) => {
      if (l.id == -1) {
        this.course_http.addLezioneProg(id_corso, id_prog, l).subscribe({
          next: (d) => {
            this.dialog.closeAll()
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
      } else {
        this.course_http.updateLezioneProg(id_corso, id_prog, l).subscribe({
          next: (d) => {
            this.dialog.closeAll()
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
    })
  }

  upload_immagine_copertina(event: any) {
    const file: File = event.target.files[0];

    if (file) {
      this.course.immagine_copertina = file;
    }
  }

  upload_file_certificato(event: any) {
    const file: File = event.target.files[0];

    if (file) {
      this.course.file_certificato = file;
    }
  }

  private padTo2Digits(num: number): string {
    return num.toString().padStart(2, '0');
  }

  formatDate(date: Date): string {
    return [
      date.getFullYear(),
      this.padTo2Digits(date.getMonth() + 1),
      this.padTo2Digits(date.getDate()),
    ].join('-');
  }

  convertDate(date: string): Date {
    const [month, day, year] = date.split('/');
    return new Date(+year, +month - 1, +day);
  }

  adjustDate(lezione: Lesson, event: MatDatepickerInputEvent<Date>): void {
    if (event.value)
      lezione.data = this.formatDate(event.value);
  }
}
