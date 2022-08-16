import { Component, Input, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { BACKEND_URL } from '../globals';

@Component({
  selector: 'app-teacher-card',
  templateUrl: './teacher-card.component.html',
  styleUrls: ['./teacher-card.component.css']
})
export class TeacherCardComponent implements OnInit {
  @Input() teacher: any;
  BACKEND_URL: string = BACKEND_URL;

  constructor(private router: Router) { }

  ngOnInit(): void {
  }

  openTeacherPage() {
    this.router.navigate([`/teacher/${this.teacher.id}`])
  }
}
