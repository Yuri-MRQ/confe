def statement(tip_rel, nav, data_inicial, data_final):
    '''Receberá o tip_rel que é o tipo de relatório desejado e retornará o statament pronto para pode
    fazer o db.query. Return a db.query type
    tip_rel : Tipo de relatório pré definido desejado
    nav : Qual a OM
    
    Return db.query()'''

    if data_inicial == None:
        data_inicial = '2020/01/01'
    if data_final == None:
        data_final = '2999/01/01'
    st = ''
    if tip_rel == 'nf_total':
        if nav.lower() == 'gnho':
            
            st = ("SELECT e.nav, f.nome_fornecedor, e.n_ne, e.vl_ne, t1.disponivel, nf.n_nf, nf.data_nf, nf.vl_nf, nf.data_pg" 
                " FROM nota_fiscal AS nf" 
                " JOIN nota_empenho AS e" 
                " ON nf.n_ne = e.n_ne" 
                " JOIN fornecedores AS f" 
                " ON f.id = e.id_fornecedor"
                " JOIN (SELECT DISTINCT e.n_ne, e.vl_ne - SUM(nf.vl_nf) OVER (PARTITION BY e.n_ne) AS disponivel" 
                " FROM nota_empenho AS e"
                " JOIN nota_fiscal AS nf"
                " ON e.n_ne = nf.n_ne) AS t1"
                " ON t1.n_ne = e.n_ne"
                " WHERE nf.data_nf >= '{}' AND  nf.data_nf <= '{}'"
                " ORDER BY e.nav, f.nome_fornecedor, e.n_ne".format(data_inicial, data_final))
        else:
        
            st = ("SELECT e.nav, f.nome_fornecedor, e.n_ne, e.vl_ne, t1.disponivel, nf.n_nf, nf.data_nf, nf.vl_nf, nf.data_pg" 
                " FROM nota_fiscal AS nf" 
                " JOIN nota_empenho AS e" 
                " ON nf.n_ne = e.n_ne" 
                " JOIN fornecedores AS f" 
                " ON f.id = e.id_fornecedor"
                " JOIN (SELECT DISTINCT e.n_ne, e.vl_ne - SUM(nf.vl_nf) OVER (PARTITION BY e.n_ne) AS disponivel" 
                " FROM nota_empenho AS e"
                " JOIN nota_fiscal AS nf"
                " ON e.n_ne = nf.n_ne) AS t1"
                " ON t1.n_ne = e.n_ne"
                " WHERE LOWER(e.nav) = '{}' AND nf.data_nf >= '{}' AND  nf.data_nf <= '{}'"
                " ORDER BY e.nav, f.nome_fornecedor, e.n_ne".format(nav.lower(), data_inicial, data_final))
            
    elif tip_rel == 'nf_total_pagas':
        if nav.lower() == 'gnho':
            st = ("SELECT e.nav, f.nome_fornecedor, nf.n_nf, nf.data_nf, nf.vl_nf, nf.data_pg" 
                " FROM nota_fiscal AS nf" 
                " JOIN nota_empenho AS e" 
                " ON nf.n_ne = e.n_ne" 
                " JOIN fornecedores AS f" 
                " ON f.id = e.id_fornecedor"
                " WHERE nf.data_pg IS NOT NULL AND nf.data_pg >= '{}' AND  nf.data_pg <= '{}'"
                " ORDER BY e.nav, f.nome_fornecedor, nf.n_nf".format(data_inicial, data_final))
        else:
            st = ("SELECT e.nav, f.nome_fornecedor, nf.n_nf, nf.data_nf, nf.vl_nf, nf.data_pg" 
                " FROM nota_fiscal AS nf" 
                " JOIN nota_empenho AS e" 
                " ON nf.n_ne = e.n_ne" 
                " JOIN fornecedores AS f" 
                " ON f.id = e.id_fornecedor"
                " WHERE nf.data_pg IS NOT NULL AND LOWER(e.nav) = '{}' AND nf.data_pg >= '{}' AND  nf.data_pg <= '{}'"
                " ORDER BY e.nav, f.nome_fornecedor, nf.n_nf".format(nav.lower(), data_inicial, data_final))
    
    elif tip_rel == 'ne':
        if nav.lower() == 'gnho':
            
            st = ("SELECT e.nav, f.nome_fornecedor, e.n_ne, e.vl_ne, e.data_ne, t1.disponivel" 
                " FROM nota_empenho AS e" 
                " JOIN fornecedores AS f" 
                " ON f.id = e.id_fornecedor"
                " JOIN (SELECT DISTINCT e.n_ne, CASE WHEN (SUM(nf.vl_nf) > 0) THEN (e.vl_ne - SUM(nf.vl_nf) OVER (PARTITION BY e.n_ne))"
                " ELSE e.vl_ne END AS disponivel"
                " FROM nota_empenho AS e"
                " LEFT JOIN nota_fiscal AS nf"
                " ON e.n_ne = nf.n_ne"
                " GROUP BY e.n_ne, e.vl_ne, nf.vl_nf) AS t1"
                " ON t1.n_ne = e.n_ne"
                " WHERE e.data_ne >= '{}' AND  e.data_ne <= '{}'"
                " ORDER BY e.nav, f.nome_fornecedor, e.n_ne".format(data_inicial, data_final))
        else:
        
            st = ("SELECT e.nav, f.nome_fornecedor, e.n_ne, e.vl_ne, e.data_ne, t1.disponivel" 
                " FROM nota_empenho AS e" 
                " JOIN fornecedores AS f" 
                " ON f.id = e.id_fornecedor"
                " JOIN (SELECT DISTINCT e.n_ne, CASE WHEN (SUM(nf.vl_nf) > 0) THEN (e.vl_ne - SUM(nf.vl_nf) OVER (PARTITION BY e.n_ne))"
                " ELSE e.vl_ne END AS disponivel"
                " FROM nota_empenho AS e"
                " LEFT JOIN nota_fiscal AS nf"
                " ON e.n_ne = nf.n_ne"
                " GROUP BY e.n_ne, e.vl_ne, nf.vl_nf) AS t1"
                " ON t1.n_ne = e.n_ne"
                " WHERE LOWER(e.nav) = '{}' AND e.data_ne >= '{}' AND  e.data_ne <= '{}'"
                " ORDER BY e.nav, f.nome_fornecedor, e.n_ne".format(nav.lower(), data_inicial, data_final))
    return st