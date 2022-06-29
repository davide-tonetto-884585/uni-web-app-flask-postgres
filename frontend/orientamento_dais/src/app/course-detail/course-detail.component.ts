import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';

import { CourseHttpService } from '../course-http.service';
import { UserHttpService } from '../user-http.service';
import { Router, ActivatedRoute } from '@angular/router';
import { Course, ProgCourse, Lesson, Aula } from '../models';
import { MessageDialogComponent } from '../message-dialog/message-dialog.component';
import { BACKEND_URL } from '../globals';

@Component({
  selector: 'app-course-detail',
  templateUrl: './course-detail.component.html',
  styleUrls: ['./course-detail.component.css']
})
export class CourseDetailComponent implements OnInit {
  private course_id: any;
  course: Course | undefined;
  docenti: any[] = [];
  prog_corso: ProgCourse[] = [];
  BACKEND_URL: string = BACKEND_URL;

  constructor(
    private course_http: CourseHttpService,
    private activatedRoute: ActivatedRoute,
    private user_http: UserHttpService,
    public dialog: MatDialog
  ) { }

  ngOnInit(): void {
    this.activatedRoute.paramMap.subscribe(params => {
      this.course_id = params.get('id');
    });

    this.course_http.getCourse(this.course_id).subscribe({
      next: (course: Course) => {
        this.course = course;
      }
    });

    this.course_http.getDocentiCorso(this.course_id).subscribe({
      next: (docenti) => {
        this.docenti = docenti;
      }
    });

    this.course_http.getProgrammazioniCorso(this.course_id).subscribe({
      next: (prog_corso: ProgCourse[]) => {
        this.prog_corso = prog_corso;

        this.prog_corso.forEach((el: ProgCourse) => {
          this.course_http.getLezioniProgCorso(this.course_id, el.id).subscribe({
            next: (lezioni: Lesson[]) => {
              el.lezioni = lezioni;

              el.lezioni.forEach((les: Lesson) => {
                if (les.id_aula) {
                  this.course_http.getAula(les.id_aula).subscribe({
                    next: (aula: Aula) => {
                      les.aula = aula;
                    }
                  });
                }
              });
            }
          });

          this.course_http.getIscrittiProgCorso(this.course_id, el.id).subscribe({
            next: (iscritti) => {
              el.iscritti = iscritti;
            }
          })
        });
      }
    });
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

  enrollStudent(id_prog_corso: number) {
    let id_stud = this.user_http.getId()
    if (id_stud) {
      this.course_http.enrollStudent(this.course_id, id_prog_corso, id_stud).subscribe({
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

  isAlreadyInscripted(): boolean {
    //TODO: completare

    return false;
  }
}
