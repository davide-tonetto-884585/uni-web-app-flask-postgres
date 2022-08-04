import { Component, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MessageDialogComponent } from '../message-dialog/message-dialog.component';

import { Question } from '../models';
import { QuestionsHttpService } from '../questions-http.service';
import { UserHttpService } from '../user-http.service';

@Component({
  selector: 'app-question-item',
  templateUrl: './question-item.component.html',
  styleUrls: ['./question-item.component.css']
})
export class QuestionItemComponent implements OnInit {
  @Input() question: Question | undefined;
  @Input() docenti_corso: any[] = [];
  replies: Question[] = [];
  answer_text: string = '';
  utenti_like: any[] = [];

  constructor(
    private user_http: UserHttpService,
    private question_http: QuestionsHttpService,
    private dialog: MatDialog
  ) { }

  ngOnInit(): void {
    this.reloadLike();
  }

  reloadLike(): void {
    if (this.question)
      this.question_http.getLikeDomanda(this.question?.id_corso, this.question?.id).subscribe({
        next: (res) => {
          this.utenti_like = res;
        }
      })
  }

  isLogged(): boolean {
    return this.user_http.isLogged();
  }

  alreadyLiked(): boolean {
    let res = false;

    this.utenti_like.every((utente) => {
      if (utente.id == this.user_http.getId()) {
        res = true;
        return false;
      }

      return true;
    })

    return res;
  }

  addLikeDomanda(): void {
    if (this.question)
      this.question_http.addLikeDomanda(this.question?.id_corso, this.question?.id).subscribe({
        next: (res) => {
          if (this.question && this.question.total_likes != null) {
            this.question.total_likes++;
          }
          this.reloadLike();
        }
      })
  }

  canAnswer(): boolean {
    let res: boolean = false;
    if (this.user_http.getId() && !this.question?.chiusa) {
      if (this.user_http.getId() === this.question?.id_utente)
        res = true;

      this.docenti_corso.every((docente) => {
        if (docente.id === this.user_http.getId()) {
          res = true;
          return false;
        }

        return true;
      })
    }

    return res;
  }

  loadReplies(): void {
    if (this.question)
      this.question_http.getRisposteDomanda(this.question?.id_corso, this.question?.id).subscribe({
        next: (res) => {
          this.replies = res;
        }
      })
  }

  postAnsware(): void {
    if (this.answer_text == '') return;

    this.question_http.addDomandaCorso({
      id_corso: this.question?.id_corso,
      id_utente: this.user_http.getId(),
      testo: this.answer_text,
      id_domanda_corso: this.question?.id
    }).subscribe({
      next: (res) => {
        this.answer_text = '';
        this.loadReplies();
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

  chiudiDomanda(): void {
    if (this.question)
      this.question_http.closeDomanda(this.question?.id_corso, this.question?.id).subscribe({
        next: (res) => {
          if (this.question)
            this.question.chiusa = true;
        }
      })
  }
}
