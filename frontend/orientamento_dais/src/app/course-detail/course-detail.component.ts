import { Component, OnInit } from '@angular/core';

import { CourseHttpService } from '../course-http.service';
import { UserHttpService } from '../user-http.service';
import { Router, ActivatedRoute } from '@angular/router';
import { Course, ProgCourse, Lesson, Aula } from '../models';

@Component({
  selector: 'app-course-detail',
  templateUrl: './course-detail.component.html',
  styleUrls: ['./course-detail.component.css']
})
export class CourseDetailComponent implements OnInit {
  private course_id: any;
  course: Course | undefined;
  docenti: any;
  prog_corso: ProgCourse[] | undefined;

  constructor(
    private course_http: CourseHttpService,
    private activatedRoute: ActivatedRoute,
    private user_http: UserHttpService
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
        });
      }
    });
  }

  isLogged() {
    return this.user_http.isLogged();
  }

  isStudent() {
    return this.user_http.isStudent();
  }
}
