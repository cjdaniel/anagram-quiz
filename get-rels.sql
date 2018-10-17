select
--  parents.word as parent,
  children.word as child
from rels
  inner join words as parents
    on rels.parent = parents.rowid
  inner join words as children
    on rels.child = children.rowid
where parents.word = 'rift'
;
