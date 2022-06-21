import { Component, OnInit } from '@angular/core';

import { CourseHttpService } from '../course-http.service';
import { Router, ActivatedRoute } from '@angular/router';
import { Course } from '../models';

@Component({
  selector: 'app-course-detail',
  templateUrl: './course-detail.component.html',
  styleUrls: ['./course-detail.component.css']
})
export class CourseDetailComponent implements OnInit {
  private course_id: any;
  course: Course | undefined;

  constructor(
    private course_http: CourseHttpService,
    private activatedRoute: ActivatedRoute,
  ) { }

  ngOnInit(): void {
    this.activatedRoute.paramMap.subscribe(params => {
      this.course_id = params.get('id');
    });

    this.course_http.getCourse(this.course_id).subscribe({
      next: (course: Course) => {
        this.course = course;
      }
    })
  }
}
