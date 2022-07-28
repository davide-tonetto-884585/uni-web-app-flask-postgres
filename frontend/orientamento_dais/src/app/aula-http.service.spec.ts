import { TestBed } from '@angular/core/testing';

import { AulaHttpService } from './aula-http.service';

describe('AulaHttpService', () => {
  let service: AulaHttpService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AulaHttpService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
