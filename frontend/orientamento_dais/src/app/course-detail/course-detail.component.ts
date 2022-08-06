import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';

import { CourseHttpService } from '../course-http.service';
import { UserHttpService } from '../user-http.service';
import { Router, ActivatedRoute } from '@angular/router';
import { Course, ProgCourse, Lesson, Aula, Question } from '../models';
import { MessageDialogComponent } from '../message-dialog/message-dialog.component';
import { BACKEND_URL } from '../globals';
import { QuestionsHttpService } from '../questions-http.service';
import { PageEvent } from '@angular/material/paginator';

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
  questions: Question[] = [];
  BACKEND_URL: string = BACKEND_URL;

  question_text: string = '';
  search_text: string | null = '';
  chiusa: string | null = null;
  order_by: string = 'like';

  limit: number = 10;
  skip: number = 0;
  count: number = 0;  

  constructor(
    private course_http: CourseHttpService,
    private activatedRoute: ActivatedRoute,
    private user_http: UserHttpService,
    private question_http: QuestionsHttpService,
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

    this.loadProgs(true);

    this.question_http.getDomandeCorso(this.course_id, null, null, this.skip, this.limit, 'like').subscribe({
      next: (res) => {
        this.questions = res.domande;
        this.count = res.count;
      }
    })
  }

  loadProgs(in_corso: boolean | null): void {
    this.course_http.getProgrammazioniCorso(this.course_id, in_corso).subscribe({
      next: (prog_corso: ProgCourse[]) => {
        this.prog_corso = prog_corso;
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

  filter(): void {
    if (this.search_text == '') this.search_text = null;

    let chiusa = null;
    if (this.chiusa == '1') chiusa = true;
    else if (this.chiusa == '0') chiusa = false;

    this.question_http.getDomandeCorso(this.course_id, this.search_text, chiusa, this.skip, this.limit, this.order_by).subscribe({
      next: (res) => {
        this.questions = res.domande;
        this.count = res.count;
      }
    })
  }

  postQuestion(): void {
    if (this.question_text == '') return;
    
    this.question_http.addDomandaCorso({
      id_corso: this.course_id, 
      id_utente: this.user_http.getId(),
      testo: this.question_text,
    }).subscribe({
      next: (res) => {
        this.question_text = '';
        this.filter();
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

  onPageChange(pageEvent: PageEvent): void {
    this.limit = pageEvent.pageSize
    this.skip = pageEvent.pageIndex * this.limit;
    this.filter();
  }
}
